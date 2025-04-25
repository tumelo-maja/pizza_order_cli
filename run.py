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

PIZZA_MENU = {
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
    "6": {"name": "Mango Juice 330ml", "price": 1.60},
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

PIZZA_SIZES = {
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

ORDER_NUMBER_LENGTH =12

class Pizza():
    """
    Creates a Pizza instance
    """

    def __init__(self, name, base_toppings, size, base_price, toppings,dips,sides,drinks):
        self.name = name
        self.base_toppings = base_toppings
        self.size = size
        self.base_price = base_price
        self.toppings = toppings
        self.dips = dips
        self.sides = sides
        self.drinks = drinks

    def summary(self):
        topping_str = f"Topping(s):{self.toppings['counts']}" if self.toppings['counts'] > 0 else ''
        description_str = f"1x {self.name} {self.size}\U0001F355- {topping_str}, Sides:10, Drink(s):12"
        price_str = f"£{'{:.2f}'.format(self.total_price)}"
        return description_str, price_str
    

    @property
    def total_price(self):
        
        toppings_prices = [EXTRA_TOPPINGS[x[0]]['price']*x[1] for x in self.toppings['item_indx']]
        dips_prices = [EXTRA_DIP[x[0]]['price']*x[1] for x in self.dips['item_indx']]
        sides_prices = [SIDES_MENU[x[0]]['price']*x[1] for x in self.sides['item_indx']]
        drinks_prices = [DRINKS_MENU[x[0]]['price']*x[1] for x in self.drinks['item_indx']]
        
        items_total = (self.base_price + 
                       sum(toppings_prices) + 
                       sum(dips_prices) +
                       sum(sides_prices) +
                       sum(drinks_prices)
                       )
        return round(items_total, 2)


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
        BASE_PIZZA_PREP_TIME = 15
        DELAY_PIZZA_PREP_TIME = 5

        preparation_time = 0
        for i, order_item in enumerate(self.order_list):

            if i == 0:
                preparation_time += BASE_PIZZA_PREP_TIME
            else:
                preparation_time += DELAY_PIZZA_PREP_TIME

            if order_item.toppings['counts'] > 5:
                preparation_time += DELAY_PIZZA_PREP_TIME

        ready_by_time = datetime.strptime(
            self.order_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=preparation_time)

        return ready_by_time.replace(second=0).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def order_items(self):

        full_order_str = []
        for order_item in self.order_list:

            size_str = order_item.size.split(' - ')[0]
            name_str = order_item.name
            topping_count = order_item.toppings['counts']

            topping_str = f" - extra toppings: {topping_count}" if topping_count > 0 else ''

            full_order_str.append(f"1 x {size_str} {name_str}{topping_str}")

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
        # add some code later
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
    SHEET = GSPREAD_CLIENT.open('pizza_order_cli_gs')

    sheet_object = SHEET.worksheet(sheet_name)

    return sheet_object


def create_order(pizza_list=[]):
    """
    Creates new pizza order from user's inpusts 

    Returns
    -------
    Pizza object.

    """
    continue_order = True
    while continue_order:
        # choose pizza name
        pizza_name, pizza_base = choose_pizza_name()

        # choose pizza size
        pizza_size, pizza_price = choose_pizza_size()

        # Choose extra toppigns
        pizza_toppings = choose_extra_items('toppings')

        # Choose extra dips
        dips = choose_extra_items('Dips')
        
        # Choose sides
        sides = choose_extra_items('sides')

        # Choose drinks
        drinks = choose_extra_items('drinks')

        pizza_object = Pizza(name=pizza_name,
                             base_toppings=pizza_base,
                             size=pizza_size,
                             base_price=pizza_price,
                             toppings=pizza_toppings,
                             dips=dips,
                             sides=sides,
                             drinks=drinks)
        
        # Print summary
        print_pizza_summary(pizza_object)

        pizza_list.append(pizza_object)
        
        while True:
            print("\nWould you like to add another pizza? \n1) Yes \n2) No")
            add_more_pizza = input("Enter your choice:\n")
            if validate_single_entry(add_more_pizza,1,2):
                break

        if add_more_pizza == '2':
            continue_order = False

    return pizza_list


def choose_pizza_name():
    indent_value=20
    print("\nChoose your Pizza (one pizza at a time):\n")
    print("Our Pizza's'".ljust(indent_value) + "| Base toppings")
    print("-"*35)
    
    while True:
        for key, value in PIZZA_MENU.items():
            print(f"{key}) {value['name']}".ljust(indent_value) + f"| {', '.join(value['base_toppings'])}")
            
        pizza_ind = input("Enter your choice:\n")
        if validate_single_entry(pizza_ind,1,5):
            break
    pizza_name = PIZZA_MENU[pizza_ind]['name']
    pizza_base = PIZZA_MENU[pizza_ind]['base_toppings']
    return pizza_name, pizza_base


def choose_pizza_size():
    indent_value=20
    while True:
        print("\nChoose the Pizza size:")
        print("-"*35)
        for key, value in PIZZA_SIZES.items():
            print(f"{key}) {value['label']}".ljust(indent_value) + f"| £{value['price']}")
        size_ind = input("Enter your choice:\n")
        if validate_single_entry(size_ind,1,3):
            break
    pizza_size = PIZZA_SIZES[size_ind]['label']
    pizza_price = PIZZA_SIZES[size_ind]['price']
    return pizza_size, pizza_price


def choose_extra_items(item_type):
    
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
        
        
    while True:
        print(f"\nAny {item_type}? (input(s) can be comma-separated integers):")
        for key, value in menu_list.items():
            if key == "0":
                print(f"{key}) {value}")
            else:
                print(f"{key}) {value['name']}" + f"| £{value['price']}")
                
        item_ind_list = input("Enter your choice(s):\n")
        if validate_multiple_entries(item_ind_list,0,len(menu_list)-1):
            break
        
    extra_items = [menu_list[x]['name'] for x in item_ind_list.split(",") if x != "0"]
    extra_items_indx = [x for x in item_ind_list.split(",") if x != "0"]
  
    extra_items_dict = {'labels': [f"{count} x {item}" if extra_items != ["None"] else None for item, count in Counter(extra_items).items()],
                        'item_indx': [[f"{item}",count] if extra_items != ["None"] else None for item, count in Counter(extra_items_indx).items()],
                      'counts': len(extra_items)}

    return extra_items_dict    
   

def print_pizza_summary(pizza_object):
    print("\nOrder summary: ")
    summary_str = f"1) {pizza_object.size} {pizza_object.name} pizza with "
    if pizza_object.toppings['counts'] >0:
        print(summary_str + "the following extra toppings:")
        print(" " + "\n ".join(pizza_object.toppings['labels']))
    else:
        print(summary_str + "no extra toppings")
        
        # pizza_object = Pizza(name=pizza_name,
        #                      base_toppings=pizza_base,
        #                      size=pizza_size,
        #                      base_price=pizza_price,
        #                      toppings=pizza_toppings,
        #                      dips=dips)


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
        input("- Press any key to return to pizza selection\n")
        total_sum=0
        order_comfirmed="2"

    else:
        
        while True:
            print("\nConfirm your full order:")
            total_sum = 0
            for order in input_list:
                description_str, price_str = order.summary()
                print(f"{description_str}".ljust(65) + f"| {price_str}")
                total_sum += order.total_price
            total_sum = round(total_sum, 2)
            print('-'*73)
            print("Total cost:".ljust(65) + f"| £{'{:.2f}'.format(total_sum)}")
            print("\n1) Place order")
            print("2) Add more items")
            print("3) Remove items")
            order_comfirmed = input("Enter your choice:\n")
            if validate_single_entry(order_comfirmed,1,3):
                break
        
    return order_comfirmed, total_sum

def print_order_summary(order_dict):
    print("Here's your order summary:\n")

    new_labels = ['Order number','Order time','Ordered items','Collection time','Order status','Total']
    
    indent_value= 20
    
    for label,value in zip(new_labels,order_dict):
        
        if label== 'Total':
            value = value if isinstance(value, str) else f"£{'{:.2f}'.format(value)}"
            
        if 'time' in label:
            print("Order date".ljust(indent_value) + f"| {value.split(' ')[0]}")
            value = value.split(' ')[1][:-3]

        
        if label =='Ordered items' and ',' in value:
            align_space = " " * len(f"{label}".ljust(indent_value)) + "|"
            split_str = value.split(',')
            
            print(f"{label}".ljust(indent_value) + f"| {split_str[0]}\n{align_space} " + f'\n{align_space}'.join(split_str))
            
        else: 
            print(f"{label}".ljust(indent_value) + f"| {value}")




def update_orders_sheet(order,worksheet):
    print("Updating 'order' worksheet...")
    
    order_list_item = list(order.summary.values())
    
    worksheet.append_row(order_list_item)

    print("'orders' worksheet updated successfully.")
    print("\nThank you for sending your order. It is now being prepared...")
    print_order_summary(order.summary.values())

    
    while True:
        print("\n1) Return to home page")
        print("2) Quit application")
        end_response= input("Enter your choice:\n")
        if validate_single_entry(end_response,1,2):
            break
    
    if end_response== "1":
        return True
    else:
        return False


def get_latest_order_ID(orders_sheet):
    latest_order_ID = orders_sheet.col_values(1)[-1]
    today_date = datetime.today().strftime("%Y%m%d")
    
    if today_date not in latest_order_ID:
        last_orderID = 0
    else:
        last_orderID= int(latest_order_ID[-4:])
        
    return last_orderID

def prepare_new_order(last_orderID):

    pizza_list=[]
    continue_loop= 1
    
    while continue_loop:
        
        if continue_loop == 1:
            pizza_list= create_order(pizza_list)
            
            total_price, continue_loop  = confirm_order(pizza_list)
        
        elif continue_loop == 2:
            continue_loop =1
            continue
        elif continue_loop == 3:
            pizza_list = remove_order_items(pizza_list)
            order_comfirmed, total_price= summary_order_confirm(pizza_list)
          
            if order_comfirmed == "1":
                continue_loop=0
            elif order_comfirmed == "2":
                continue_loop=1
            elif order_comfirmed == "3":
                pass
            else:
                print("Invalid input")            

    order = Order(pizza_list, total_price, last_orderID)
    return order

def remove_order_items(input_list):
    
    indent_value= 60
    while True:
        print("\nSelect the order item(s) you wish to remove \n(inputs can be comma-separated integers)")
        for ind, order in enumerate(input_list):
            description_str, price_str = order.summary()
            print(f"{ind+1}) {description_str}".ljust(indent_value) + f"| {price_str}")
        remove_items= input("Enter your choice:\n")
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
        
def validate_multiple_entries(values_input, min_value=None, max_value=None):
    
    try:
        values = [x for x in values_input.split(",")]
        
        # 1) Check if zeros in included with outher numbers
        if len(values)> 1 and '0' in values:
                raise ValueError(f"'{values_input}' is not a valid entry. You cannot select '0' with any other values")
        
        # 2) Check if there are any spaces ' '
        if ' ' in values_input:
            raise ValueError(f"'{values_input}' is not a valid entry. The input value must not contain any spaces")

        for value in values:
            
            # 3) Check if there are leading zerpos
            if len(value)> 1 and value.startswith("0"):
                    raise ValueError(f"'{value}' is not a valid entry. Leading zeros are not allowed")
            
            # 4) Check if digit
            if not value.isdigit():
                raise ValueError(f"'{value}' is not an integer. The input values must be between {min_value} and {max_value}")
            value = int(value)
            
            # 5 check if within range
            if value < min_value or value>max_value:
                raise ValueError(f"Value '{value}' is out of range. The input values must be between {min_value} and {max_value}")

    except ValueError as e:
        print(f"\nInvalid entry: {e}, please try again.\n")
        return False

    return True

def welcome_page():
    
    dashes = "-"*19
    welcome_str = f"/{dashes} \U0001F355   Welcome to PizzaPalace CLI!   \U0001F355 {dashes}\\"
    second_line_str = "|---  Packed with incredible flavors - our pizzas are irresitably tasty! ---|"
    # print(f"welcome_str: {len(welcome_str)}")
    # print(f"second_line_str: {len(second_line_str)}")
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
    
        task_to_do = input("Enter your choice:\n")
        if validate_single_entry(task_to_do,0,2):
            break
    return task_to_do        

def track_order(orders_sheet):
    
    while True:
        print("Track order:")
        order_number = input("Enter your order number or '99' to return to home page:\n")
        if order_number == '99':
            return True
        elif validate_order_number(order_number):
            break
    
    order_number= int(order_number)
    orders_df = pd.DataFrame(orders_sheet.get_all_records())
    
    update_orders_status(orders_sheet,orders_df)
    orders_df = pd.DataFrame(orders_sheet.get_all_records())
    order_index = orders_df[orders_df['Order ID'] == order_number].index
    
    order_dict = orders_df.iloc[order_index[0]].to_dict()

    status_str, order_dict = check_order_status(order_dict)     
    
    print(f"Chosen one: {order_dict.values()}")
    print(order_dict.values())

    print_order_summary(order_dict.values())
    print(f"\n{status_str}")
    
    while True:
        print("1) Return to home page")
        print("2) Quit application")
        end_response= input("Enter your choice:\n")
        if validate_single_entry(end_response,1,2):
            break
    
    if end_response== "1":
        return True
    else:
        return False

def update_orders_status(orders_sheet,orders_df):
    print("Updating orders...")
    
    for ind, row in orders_df.iterrows():
        status_column = row['Order ready time']
        
        if status_column != 'Ready':
            
            time_format ="%Y-%m-%d %H:%M:%S"
            current_time = datetime.now()
            ready_time = datetime.strptime(status_column,time_format)
            
            time_difference =int((current_time -ready_time).total_seconds())
            
            if time_difference > 0:
                
                orders_sheet.update_cell(ind+2, 5, 'Ready')      

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

def main():
    """
    Run the application to initiate requests for user input
    """    
    orders_sheet = connect_google_sheets('orders')        

    continue_app=True
    while continue_app:
        
        user_choice = welcome_page()
        
        if user_choice == "1":
            
            last_orderID = get_latest_order_ID(orders_sheet)
            order = prepare_new_order(last_orderID)
    
            continue_app= update_orders_sheet(order, orders_sheet)
        elif user_choice == "2":
            continue_app = track_order(orders_sheet)
        else:
            continue_app=False

main()





    