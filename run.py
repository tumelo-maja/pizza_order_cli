import gspread
from google.oauth2.service_account import Credentials
from collections import Counter
from datetime import datetime, timedelta
import pandas as pd

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

Meal_MENU = {
    "1": {"name": "Hawaiian", "base_toppings": ["ham", "pineapple", "cheese"]},
    "2": {"name": "Pepperoni", "base_toppings": ["pepperoni", "cheese", "tomato sauce"]},
    "3": {"name": "Vegetarian", "base_toppings": ["mushrooms", "peppers", "onions", "olives"]},
    "4": {"name": "All Meaty", "base_toppings": ["pepperoni", "sausage", "ham", "bacon", "beef"]},
    "5": {"name": "Spicy Chicken", "base_toppings": ["spicy chicken", "jalapenos", "onions", "cheese"]},
}

DRINKS_MENU = {
    "0": "None",
    "1": {"name": "Coke Zero 330ml", "price": 1.20},
    "2": {"name": "Coke 330ml", "price": 1.30},
    "3": {"name": "Sprite 330ml", "price": 1.30},
    "4": {"name": "Pepsi 330ml", "price": 1.20},
    "5": {"name": "Apple Juice 330ml", "price": 1.50},
    "6": {"name": "Mango Juice 330ml", "price": 1.50},
    "7": {"name": "Orange Juice 330ml", "price": 1.50},
    "8": {"name": "Still Water 500ml", "price": 1.00},
}

EXTRA_TOPPING_PRICE = 1.50
EXTRA_TOPPINGS = {
    "0": "None",
    "1": {"name": "Mushrooms", "price": EXTRA_TOPPING_PRICE},
    "2": {"name": "Mixed Peppers", "price": EXTRA_TOPPING_PRICE},
    "3": {"name": "Jalapenos", "price": EXTRA_TOPPING_PRICE},
    "4": {"name": "Cheese", "price": EXTRA_TOPPING_PRICE},
    "5": {"name": "Pepperoni", "price": EXTRA_TOPPING_PRICE},
    "6": {"name": "Chicken", "price": EXTRA_TOPPING_PRICE},
    "7": {"name": "Beef", "price": EXTRA_TOPPING_PRICE},
    "8": {"name": "Bacon", "price": EXTRA_TOPPING_PRICE},
}

EXTRA_DIP_PRICE = 0.60
EXTRA_DIP = {
    "0": "None",
    "1": {"name": "Garlic & Herb Dip", "price": EXTRA_DIP_PRICE},
    "2": {"name": "BBQ Dip", "price": EXTRA_DIP_PRICE},
    "3": {"name": "Sriracha Dip", "price": EXTRA_DIP_PRICE},
    "4": {"name": "Ranch Dip", "price": EXTRA_DIP_PRICE},
}

SIDES_PRICE = 1.50
SIDES_MENU = {
    "0": "None",
    "1": {"name": "Small Fries", "price": 1.80},
    "2": {"name": "Medium Fries", "price": 2.30},
    "3": {"name": "Large Fries", "price": 2.80},
    "4": {"name": "8 x Chicken Wings", "price": 4.50},
    "5": {"name": "12 x Chicken Wings", "price": 6.50},
    "6": {"name": "16 x Chicken Wings", "price": 8.00},
}

Meal_SIZES = {
    "1": {
        "label": 'Small',
        "size_inch": '9"',
        "size_cm": '23 cm',
        "price": 9.00
    },
    "2": {
        "label": 'Medium',
        "size_inch": '12"',
        "size_cm": '30 cm',
        "price": 11.00
    },
    "3": {
        "label": 'Large',
        "size_inch": '15"',
        "size_cm": '38 cm',
        "price": 15.00
    }
}

EXTRAS_NAMES=(('toppings','TPs'),('dips','DPs'),('sides','SDs'),('drinks','DKs'))

ORDER_NUMBER_LENGTH =12

class Meal():
    """
    Creates a Meal instance
    """

    def __init__(self, pizza_name, pizza_base_toppings, pizza_size, pizza_price, toppings,dips,sides,drinks,quantity):
        self.pizza_name = pizza_name
        self.pizza_base_toppings = pizza_base_toppings
        self.pizza_size = pizza_size
        self.pizza_price = pizza_price
        self.toppings = toppings
        self.dips = dips
        self.sides = sides
        self.drinks = drinks
        self.quantity = quantity

    def summary(self):
        
        description_str = f"{self.quantity} x {self.pizza_name} {self.pizza_size}\U0001F355{self.extras_summary()}"
        price_str = self.total_price
        return description_str, price_str

    @property
    def total_price(self):
        
        toppings_prices = [EXTRA_TOPPINGS[x[0]]['price']*x[1] for x in self.toppings['item_indx']]
        dips_prices = [EXTRA_DIP[x[0]]['price']*x[1] for x in self.dips['item_indx']]
        sides_prices = [SIDES_MENU[x[0]]['price']*x[1] for x in self.sides['item_indx']]
        drinks_prices = [DRINKS_MENU[x[0]]['price']*x[1] for x in self.drinks['item_indx']]
        
        items_total = self.quantity * (self.pizza_price + 
                       sum(toppings_prices) + 
                       sum(dips_prices) +
                       sum(sides_prices) +
                       sum(drinks_prices)
                       )
        return round(items_total, 2)
    
    def extras_summary(self,label_type='short'):
        
        extras_str_list=[]
        for extra_full,extra_short in EXTRAS_NAMES:
            extra_counts =getattr(self, extra_full).get('counts')
            if extra_counts>0:
                if label_type == 'full':
                    extras_str_list.append(f"{extra_full}:{extra_counts}")
                else:
                    extras_str_list.append(f"*{extra_short}:{extra_counts}")


        extras_str = f" - {' '.join(extras_str_list)}" if len(extras_str_list) > 0 else ''
        
        return extras_str

class Order():
    """
    Creates an instance order.
    """

    def __init__(self, order_list, total_price,last_orderID):
        self.order_list = order_list
        self.total_price = total_price
        self.order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_orderID = last_orderID
        self.order_ID = self.create_order_ID()

    @property
    def order_ready_time(self):
        BASE_MEAL_PREP_TIME = 15
        DELAY_Meal_PREP_TIME = 5
    
        Meal_count = sum([x.quantity for x in self.order_list])
        topping_sides = sum([x.toppings['counts']+x.sides['counts'] for x in self.order_list])
        preparation_time = BASE_MEAL_PREP_TIME
    
        if Meal_count > 2:
            preparation_time += ((Meal_count // 5) * DELAY_Meal_PREP_TIME)+DELAY_Meal_PREP_TIME
    
        if topping_sides > 0:
            preparation_time += ((topping_sides // 5) * DELAY_Meal_PREP_TIME)+DELAY_Meal_PREP_TIME
    
        ready_by_time = datetime.strptime(self.order_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=preparation_time)
            
        return ready_by_time.replace(second=0).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def order_items(self):

        full_order_str = []
        for order_item in self.order_list:

            size_str = order_item.pizza_size.split(' - ')[0]
            name_str = order_item.pizza_name

            full_order_str.append(f"{order_item.quantity} x {size_str} {name_str}{order_item.extras_summary('full')}")

        return ', '.join(full_order_str)

    @property
    def summary(self):

        return {
            "Order ID": self.order_ID,
            "Order date": self.order_date,
            "Order items": self.order_items,
            "Order ready time": self.order_ready_time,
            "Order status": 'Preparing',
            "Order total": self.total_price,
        }

    def create_order_ID(self):
        new_order_ID = datetime.today().strftime("%Y%m%d") + '{:04}'.format(self.last_orderID+1)
        
        return new_order_ID

def connect_google_sheets(sheet_name):
    """
    Setup and connects API to the google sheet and links the input 'sheet_name'

    Parameters
    ----------
    sheet_name : TYPE
        Google worksheet

    Returns
    -------
    sheet_object : TYPE
        worksheet object

    """

    CREDS = Credentials.from_service_account_file('creds.json')
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    SHEET = GSPREAD_CLIENT.open('meal_order_cli_gs')

    sheet_object = SHEET.worksheet(sheet_name)

    return sheet_object

def create_order(meal_list=[]):
    """
    Creates new Meal order from user's inpusts 

    Returns
    -------
    Meal object.

    """
    continue_order = True
    while continue_order:
        # choose Meal name
        pizza_name, pizza_base = choose_pizza_name()

        # choose Meal size
        pizza_size, pizza_price = choose_pizza_size()

        # Choose extra toppigns
        pizza_extra_toppings = choose_extra_items('toppings',8)

        # Choose extra dips
        dips = choose_extra_items('Dips',4)
        
        # Choose sides
        sides = choose_extra_items('sides',6)

        # Choose drinks
        drinks = choose_extra_items('drinks',8)
        
        # Repeat meals
        quantity = enter_meal_quantity()
        
        meal_object = Meal(pizza_name=pizza_name,
                             pizza_base_toppings=pizza_base,
                             pizza_size=pizza_size,
                             pizza_price=pizza_price,
                             toppings=pizza_extra_toppings,
                             dips=dips,
                             sides=sides,
                             drinks=drinks,
                             quantity=quantity
                             )
        
        # Print meal summary
        print_meal_summary(meal_object)

        meal_list.append(meal_object)
        
        while True:
            print("\nWould you like to add another meal? \n1) Yes \n2) No")
            add_more_meals = strppied_input("Enter your choice:\n")
            if validate_single_entry(add_more_meals,1,2):
                break

        if add_more_meals == '2':
            continue_order = False

    return meal_list

def choose_pizza_name():
    indent_value=18
    print("\nChoose your Meal (one Meal at a time):\n")
    print("Our Meals \U0001F355 ".ljust(indent_value-2) + "| Base toppings")
    print("-"*35)
    
    while True:
        for key, value in Meal_MENU.items():
            print(f"{key}) {value['name']}".ljust(indent_value) + f"| {', '.join(value['base_toppings'])}")
            
        Meal_ind = strppied_input("Enter your choice:\n")
        if validate_single_entry(Meal_ind,1,5):
            break
    Meal_name = Meal_MENU[Meal_ind]['name']
    Meal_base = Meal_MENU[Meal_ind]['base_toppings']
    return Meal_name, Meal_base

def choose_pizza_size():
    indent_value=18
    while True:
        print("\nChoose Meal size | Price (£)")
        print("-"*33)
        for key, value in Meal_SIZES.items():
            print(f"{key}) {value['label']}".ljust(indent_value) + "|"+ f"{price_format(value['price'])}".rjust(7))
        size_ind = strppied_input("Enter your choice:\n")
        if validate_single_entry(size_ind,1,3):
            break
    Meal_size = Meal_SIZES[size_ind]['label']
    Meal_price = Meal_SIZES[size_ind]['price']
    return Meal_size, Meal_price

def choose_extra_items(item_type,count_max):
    
    if item_type=='toppings':
        menu_list = EXTRA_TOPPINGS
        item_type = f'extra {item_type}'
    elif item_type=='Dips':
        menu_list = EXTRA_DIP 
        item_type = f'extra {item_type}'
    elif item_type=='drinks':
        menu_list = DRINKS_MENU
    elif item_type=='sides':
        menu_list = SIDES_MENU
        
    indent_value=22
    while True:
        print(f"\nAny {item_type}? (You can select up to {count_max} items,\n-  input(s) can be comma-separated integers):")
        print("Toppings".center(indent_value)+"| Price (£)")
        print("-"*30)

        for key, value in menu_list.items():
            if key == "0":
                print(f"{key}) {value}".ljust(indent_value)+ "|"+ "-".center(5))
            else:
                print(f"{key}) {value['name']}".ljust(indent_value) + "|"+ f"{price_format(value['price'])}".rjust(5))
                
        item_ind_list = strppied_input("Enter your choice(s):\n")
        if validate_multiple_entries(item_ind_list,0,len(menu_list)-1,count_max):
            break
        
    extra_items = [menu_list[x]['name'] for x in item_ind_list.split(",") if x != "0"]
    extra_items_indx = [x for x in item_ind_list.split(",") if x != "0"]
  
    extra_items_dict = {'labels': [f"{count} x {item}" if extra_items != ["None"] else None for item, count in Counter(extra_items).items()],
                        'item_indx': [[f"{item}",count] if extra_items != ["None"] else None for item, count in Counter(extra_items_indx).items()],
                      'counts': len(extra_items)}

    return extra_items_dict    
   
def enter_meal_quantity():
    
    while True:
        print("\nHow many qunatities of this meal would you like?:")

        quantity_input = strppied_input("Enter your required quantity (1-50):\n")
        if validate_single_entry(quantity_input,1,50):
            break

    return int(quantity_input)

def print_meal_summary(meal_object):
    print("\nOrder summary: ")
    summary_str = f"{meal_object.quantity} x {meal_object.pizza_size} {meal_object.pizza_name} Pizza with "
    extras =meal_object.extras_summary()
    if len(extras) >0:
        print(summary_str + "the following extra(s):")
        print_extras_description()
        indent_value=3
        
        for extra_full,extra_short in EXTRAS_NAMES:
            extra_counts =getattr(meal_object, extra_full).get('counts')
            extra_label =getattr(meal_object, extra_full).get('labels')
            if extra_counts>0:
        
                if len(extra_label) > 1:
                    align_space = " " * len(f"{extra_short}".ljust(indent_value)) + "  "                    
                    print(f"{extra_short}".ljust(indent_value) + f": {extra_label[0]}\n{align_space}" + f'\n{align_space}'.join(extra_label[1:]))
                else: 
                    print(f"{extra_short}".ljust(indent_value) + f" {extra_label[0]}")
    else:
        print(summary_str + "no extras")

def confirm_order(input_list):
    
    order_comfirmed, total_sum= summary_order_confirm(input_list)

    if order_comfirmed == "1":
        return total_sum, 0
    elif order_comfirmed == "2":
        return None, 2
    elif order_comfirmed == "3":
        return None, 3
    else:
        print("Invalid answer")

def summary_order_confirm(input_list):
    
    if not len(input_list):
        print("\nThere are no items in this order")
        input("- Press any key to return to Meal selection\n")
        total_sum=0
        order_comfirmed="2"

    else:
        
        while True:
            print("\nConfirm your full order:")
            total_sum = 0
            print("Items".center(59)+"| Price (£)")
            print("-"*70)
            price_indent=9

            for order in input_list:
                description_str, price_str = order.summary()
                print(f"{description_str}".ljust(57) +"|"+ f"{price_format(price_str)}".rjust(price_indent))
                total_sum += order.total_price
            total_sum = round(total_sum, 2)
            print('_'*69)
            print("Total cost:".ljust(59) +"|"+ f"{price_format(total_sum)}".rjust(price_indent))
            print_extras_description()
            print("\n1) Place order")
            print("2) Add more items")
            print("3) Remove items")
            order_comfirmed = strppied_input("Enter your choice:\n")
            if validate_single_entry(order_comfirmed,1,3):
                break
            
    return order_comfirmed, total_sum

def price_format(value):
    return '{:,.2f}'.format(value)

def print_order_summary(order_dict):
    print("Here's your order summary:\n")

    new_labels = ['Order ID','Time','Items','Ready time','Status','Total']
    
    indent_value= 10
    
    for label,value in zip(new_labels,order_dict):
        
        if label== 'Total':
            value = value if isinstance(value, str) else f"£ {price_format(value)}"
            
        if 'time' in label:
            print("Date".ljust(indent_value) + f"| {value.split(' ')[0]}")
            value = value.split(' ')[1][:-3]

        
        if label =='Items' and ',' in value:
            align_space = " " * len(f"{label}".ljust(indent_value)) + "|"
            split_str = value.split(',')
            
            print(f"{label}".ljust(indent_value) + f"| {split_str[0]}\n{align_space}" + f'\n{align_space}'.join(split_str[1:]))
            
        else: 
            print(f"{label}".ljust(indent_value) + f"| {value}")
            
def print_extras_description():
    extras_description = " - ".join(f"{short}: {full.capitalize()}" for full, short in EXTRAS_NAMES)
    print(f' * {extras_description}')

def update_orders_sheet(order):
    print("Updating 'order' worksheet...")
    order_list_item = list(order.summary.values())
    
    ORDERS_SHEET.append_row(order_list_item)

    print("'orders' worksheet updated successfully.")
    print("\nThank you for sending your order. It is now being prepared...")
    print_order_summary(order.summary.values())
 
    while True:
        print("\n1) Return to home page")
        print("2) Quit application")
        end_response= strppied_input("Enter your choice:\n")
        if validate_single_entry(end_response,1,2):
            break
    
    if end_response== "1":
        return True
    else:
        return False

def get_latest_order_ID():
    latest_order_ID = ORDERS_SHEET.col_values(1)[-1]
    today_date = datetime.today().strftime("%Y%m%d")
    
    if today_date not in latest_order_ID:
        last_orderID = 0
    else:
        last_orderID= int(latest_order_ID[-4:])
        
    return last_orderID

def prepare_new_order(last_orderID):

    meal_list=[]
    continue_loop= 1
    
    while continue_loop:
        
        if continue_loop == 1:
            meal_list= create_order(meal_list)
            
            total_price, continue_loop  = confirm_order(meal_list)
        
        elif continue_loop == 2:
            continue_loop =1
            continue
        elif continue_loop == 3:
            meal_list = remove_order_items(meal_list)
            order_comfirmed, total_price= summary_order_confirm(meal_list)
          
            if order_comfirmed == "1":
                continue_loop=0
            elif order_comfirmed == "2":
                continue_loop=1
            elif order_comfirmed == "3":
                pass
            else:
                print("Invalid input")            

    order = Order(meal_list, total_price, last_orderID)
    return order

def remove_order_items(input_list):
    
    indent_value= 60
    while True:
        print("\nSelect the order item(s) you wish to remove \n(inputs can be comma-separated integers)")
        for ind, order in enumerate(input_list):
            description_str, price_str = order.summary()
            print(f"{ind+1}) {description_str}".ljust(indent_value) + f"| {price_str}")
        remove_items= strppied_input("Enter your choice:\n")
        if validate_multiple_entries(remove_items,1,len(input_list)):
            break    
    removed_indexes = [int(x)-1 for x in remove_items.split(",")]
    
    new_list = [order for i, order in enumerate(input_list) if i not in removed_indexes]
    
    return new_list   

def validate_single_entry(value, min_value=None, max_value=None):
    
    try:
        
        # 1) Check if there are any spaces ' '
        if ' ' in value:
            raise ValueError(f"'{value}' is not a valid entry. The input value must not contain any spaces")
        
        # 2) Check if there are leading zerpos
        if len(value)> 1 and value.startswith("0"):
                raise ValueError(f"'{value}' is not a valid entry. Leading zeros are not allowed")
        
        # 3) Check if digit
        if not value.isdigit():
            raise ValueError(f"'{value}' is not an integer")
        value = int(value)
        
        # 5 check if within range
        if value < min_value or value>max_value:
            raise ValueError(f"Value '{value}' is out of range. The input value must be between {min_value} and {max_value}")

    except ValueError as e:
        print(f"\nInvalid entry: {e}, please try again.\n")
        return False

    return True
        
def validate_multiple_entries(values_input, min_value=None, max_value=None,count_max=None):
    
    try:
        values = [x for x in values_input.split(",")]
        
        # 1) Check if zeros in included with outher numbers
        if len(values)> 1 and '0' in values:
                raise ValueError(f"'{values_input}' is not a valid entry. You cannot select '0' with any other values")
        
        # 2) Check if there are any spaces ' '
        if ' ' in values_input:
            raise ValueError(f"'{values_input}' is not a valid entry. The input value must not contain any spaces")

        # 3) Check number of inputs does not exceed limit
        if count_max is not None and len(values) > count_max:
            raise ValueError(f"You've entered {len(values)} items, you may only add up to {count_max} items")

        for value in values:
            
            # 3) Check if there are leading zerpos
            if len(value)> 1 and value.startswith("0"):
                    raise ValueError(f"'{value}' is not a valid entry. Leading zeros are not allowed")
            
            # 4) Check if digit
            if not value.isdigit():
                raise ValueError(f"'{value}' is not an integer. The input values must be integers between {min_value} and {max_value}")
            value = int(value)
            
            # 5 check if within range
            if value < min_value or value>max_value:
                raise ValueError(f"Value '{value}' is out of range. The input values must be integers between {min_value} and {max_value}")

    except ValueError as e:
        print(f"\nInvalid entry: {e}, please try again.")
        return False

    return True

def welcome_page():
    
    dashes = "-"*19
    welcome_str = f"/{dashes} \U0001F355   Welcome to MealPalace CLI!   \U0001F355 {dashes}\\"
    second_line_str = "|---  Packed with incredible flavors - our Meals are irresitably tasty! ---|"
    print(" "+ "_"*75 )
    print(welcome_str)
    print("|"+"-"*75 +"|")
    print(second_line_str) 
    print("\\"+"_"*75 +"/")
    indent_value =21
    
    while True:
        print("\nWhat would you like to do today? \U0001F600")
        print("1) Place an order".ljust(indent_value) + "\U0001F4DD")
        print("2) Track an order".ljust(indent_value) + "\U0001F50D")
        print("0) Quit Application".ljust(indent_value) + "\U0000274C")
    
        task_to_do = strppied_input("Enter your choice:\n")
        if validate_single_entry(task_to_do,0,2):
            break
    return task_to_do        

def track_order():
    
    while True:
        print("Track order:")
        order_number = strppied_input("Enter your order number or '99' to return to home page:\n")
        if order_number == '99':
            break
        elif not validate_order_number(order_number):
            continue
        
        order_number= int(order_number)
        update_orders_status()
        orders_df = pd.DataFrame(ORDERS_SHEET.get_all_records())
        order_index = orders_df[orders_df['Order ID'] == order_number].index
        
        if not len(order_index):
            print(f"Order number {order_number} not found. Please check the number and try again.\n")
            continue
            
        order_dict = orders_df.iloc[order_index[0]].to_dict()
        status_str, order_dict = check_order_status(order_dict)     
    
        print_order_summary(order_dict.values())
        print(f"\n{status_str}")
        
        while True:
            print("\n1) Track another order")
            print("2) Return to home page")
            end_response= strppied_input("Enter your choice:\n")
            if validate_single_entry(end_response,1,2):
                break
        
        if end_response== "2":
            break

    main()

def update_orders_status():
    print("Updating order status...")
    orders_df = pd.DataFrame(ORDERS_SHEET.get_all_records())
    
    for ind, row in orders_df.iterrows():
        status_value = row['Order ready time']
        
        if status_value != 'Ready':
            
            time_format ="%Y-%m-%d %H:%M:%S"
            current_time = datetime.now()
            ready_time = datetime.strptime(status_value,time_format)
            
            time_difference =int((current_time -ready_time).total_seconds())
            
            if time_difference > 0:
                orders_df.at[ind, 'Order status'] = 'Ready'
            else:
                orders_df.at[ind, 'Order status'] = 'Preparing'

                
    status_values = [[status_str] for status_str in orders_df['Order status'].tolist()]
    ORDERS_SHEET.update(values=status_values,range_name=f'E2:E{len(status_values)+1}')

def check_order_status(order_dict):
    print("Checking your order status...")
    
    order_ready_datetime = datetime.strptime(order_dict['Order ready time'], "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    time_difference =int((current_time -order_ready_datetime).total_seconds() )
    #202504230001
    
    order_ready_datestr=order_ready_datetime.strftime("%Y-%m-%d %H:%M")
        
    if time_difference >0:
        status_str = f"Your order has been ready since {order_ready_datestr}"
    elif time_difference <0:
        status_str = f"Your order will be ready at {order_ready_datestr}"
    else:
        status_str = "Your order is ready now"
    
    return status_str, order_dict

def validate_order_number(number):
    
    try:
        # 1) Check if there are any spaces ' '
        if ' ' in number:
            raise ValueError(f"'{number}' is not a valid order number. Order number must not contain any spaces")
        
        # 2) Check if there are leading zerpos
        if not number.startswith("20"):
                raise ValueError(f"'{number}' is not a valid order number. Order number must start with '20'")
        
        # 3) Check if digit
        if not number.isdigit():
            raise ValueError(f"'{number}' is not a valid order number. Order number must contain integers only")

        # 4) Check number length
        if len(number) != ORDER_NUMBER_LENGTH:
            raise ValueError(f"Order number must have exactly 12 integers - you provided {len(number)}")
        
    except ValueError as e:
        print(f"\nInvalid entry: {e}, please try again.\n")
        return False

    return True

def strppied_input(message):
    
    return input(message).replace(' ', '')

def main():
    """
    Run the application to initiate requests for user input
    """    

    continue_app=True
    while continue_app:
        
        user_choice = welcome_page()
        
        if user_choice == "1":
            
            last_orderID = get_latest_order_ID()
            order = prepare_new_order(last_orderID)
    
            continue_app= update_orders_sheet(order)
        elif user_choice == "2":
            continue_app = track_order()
        else:
            continue_app=False
        
        if not continue_app:
            print("\nThank you for using our app. See you soon!! \U0001F609")

ORDERS_SHEET = connect_google_sheets('orders')        

main()





    