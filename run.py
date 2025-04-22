import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
from collections import Counter
from datetime import datetime, timedelta


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

EXTRA_TOPPINGS = {
    "0": "None",
    "1": "Mushrooms",
    "2": "Mixed Peppers",
    "3": "Jalapenos",
    "4": "Cheese",
    "5": "Pepperoni",
    "6": "Chicken",
    "7": "Beef",
    "8": "Bacon",
}

EXTRA_TOPPING_PRICE = 1.50

PIZZA_SIZES = {
    "1": {
        "label": 'Small - 9" (23 cm)',
        "size_inch": '9"',
        "size_cm": '23 cm',
        "price": 9.00
    },
    "2": {
        "label": 'Medium - 12" (30 cm)',
        "size_inch": '12"',
        "size_cm": '30 cm',
        "price": 11.00
    },
    "3": {
        "label": 'Large - 15" (38 cm)',
        "size_inch": '15"',
        "size_cm": '38 cm',
        "price": 15.00
    }
}


class Pizza():
    """
    Creates a Pizza instance
    """

    def __init__(self, name, base_toppings, size, base_price, extra_toppings):
        self.name = name
        self.base_toppings = base_toppings
        self.size = size
        self.base_price = base_price
        self.extra_toppings = extra_toppings

    def summary(self):
        extra_str = f"with {self.extra_toppings['counts']} extra topping(s)" if self.extra_toppings['counts'] > 0 else ''
        description_str = f"1 x {self.name} pizza, {self.size} {extra_str}"
        price_str = f"£{'{:.2f}'.format(self.total_price)}"
        return description_str, price_str

    @property
    def total_price(self):
        base_toppings_total = self.base_price + (self.extra_toppings['counts']*EXTRA_TOPPING_PRICE)
        return round(base_toppings_total, 2)


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

            if order_item.extra_toppings['counts'] > 5:
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
            topping_count = order_item.extra_toppings['counts']

            topping_str = f" - extra toppings: {
                topping_count}" if topping_count > 0 else ''

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
        pizza_name, pizza_base = choose_pizza_name(PIZZA_MENU)

        # choose pizza size
        pizza_size, pizza_price = choose_pizza_size(PIZZA_SIZES)

        # Choose extra toppigns
        pizza_toppings = choose_extra_toppings(EXTRA_TOPPINGS)

        # Print summary
        print_pizza_summary(pizza_size, pizza_name, pizza_toppings)

        pizza_object = Pizza(name=pizza_name,
                             base_toppings=pizza_base,
                             size=pizza_size,
                             base_price=pizza_price,
                             extra_toppings=pizza_toppings)

        pizza_list.append(pizza_object)
        print("\nWould you like to add another pizza: \n1) Yes \n2) No")
        add_more_pizza = input("Enter your choice: \n")

        if int(add_more_pizza) == 2:
            continue_order = False

    return pizza_list


def choose_pizza_name(PIZZA_MENU):
    print("\nChoose your Pizza (one pizza at a time):\n")
    print("Our Pizza's'".ljust(18) + "| Base toppings")
    print("-"*35)
    
    while True:
        for key, value in PIZZA_MENU.items():
            print(f"{key}) {value['name']:<13}  | {', '.join(value['base_toppings'])}")
            
        pizza_ind = input("Enter your choice: \n")
        
        if validate_single_entry(pizza_ind,1,5):
            print("Validated input:", pizza_ind)
            break
    pizza_name = PIZZA_MENU[pizza_ind]['name']
    pizza_base = PIZZA_MENU[pizza_ind]['base_toppings']
    return pizza_name, pizza_base


def choose_pizza_size(PIZZA_SIZES):
    print("\nChoose the Pizza size:")
    for key, value in PIZZA_SIZES.items():
        print(f"{key}) {value['label']:<20}  | £{value['price']}")
    size_ind = input("Enter your choice: \n")
    pizza_size = PIZZA_SIZES[size_ind]['label']
    pizza_price = PIZZA_SIZES[size_ind]['price']
    return pizza_size, pizza_price


def choose_extra_toppings(EXTRA_TOPPINGS):
    
    while True:
        print("\nAny extra toppings? (input(s) can be comma-separated integers): ")
        for key, value in EXTRA_TOPPINGS.items():
            print(f"{key}) {value:<20}")
        toppings_ind_list = input("Enter your choice(s): \n")
        
        if validate_multiple_entries(toppings_ind_list,0,8):
            print("Validated input:", toppings_ind_list)
            break        
    toppings_items = [EXTRA_TOPPINGS[x] for x in toppings_ind_list.split(",") if x != "0"]
  
    pizza_toppings = {'labels': [f"{count} x {item}" if toppings_items != ["None"] else None for item, count in Counter(toppings_items).items()  ],
                      'counts': len(toppings_items)}

    return pizza_toppings


def print_pizza_summary(pizza_size, pizza_name, pizza_toppings):
    print("\nOrder summary: ")
    summary_str = f"1) {pizza_size} {pizza_name} pizza with "
    if pizza_toppings['counts'] >0:
        print(summary_str + "the following extra toppings:")
        print(" " + "\n ".join(pizza_toppings['labels']))
    else:
        print(summary_str + "no extra toppings")


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
        input("- Press any key to return to pizza selection \n")
        total_sum=0
        order_comfirmed="2"

    else:
            
        print("\nConfirm your full order:")
        total_sum = 0
        for order in input_list:
            description_str, price_str = order.summary()
            print(f"{description_str:<70}| {price_str}")
            total_sum += order.total_price
        total_sum = round(total_sum, 2)
        print('-'*78)
        print("Total cost:".ljust(70) + f"| £{'{:.2f}'.format(total_sum)}")
        print("1) Place order")
        print("2) Add more items")
        print("3) Remove items")
        order_comfirmed = input("Enter your choice: \n")
    
    return order_comfirmed, total_sum

def order_placed(order):
    print("\nThank you for sending your order. It is now being prepared...")
    print("Here's your order summary:\n")

    order_summary = order.summary
    new_labels = ['Order number','Order time','Ordered items','Collection time','Order status','Total']
    
    for label,value in zip(new_labels,order_summary.values()):
        
        if label== 'Total':
            value = f"£{'{:.2f}'.format(value)}"
            
        if 'time' in label:
            value = value.split(' ')[1][:-3]
        
        if label =='Ordered items' and ',' in value:
            align_space = " " * len(f"{label}".ljust(18)) + "|"
            split_str = value.split(',')
            
            print(f"{label}".ljust(18) + f"| {split_str[0]}\n{align_space} " + f'\n{align_space}'.join(split_str))
            
        else: 
            print(f"{label}".ljust(18) + f"| {value}")




def update_orders_sheet(order):
    print("Updating 'order' worksheet...")
    
    worksheet = connect_google_sheets('orders')

    order_list_item = list(order.summary.values())
    
    worksheet.append_row(order_list_item)

    print("'orders' worksheet updated successfully.")
    
    order_placed(order)
    
    print("\n0) Return to home page")
    print("q) Quit application")
    end_response= input("Enter your choice: \n")
    
    if end_response== "0":
        return True
    elif end_response.lower()=="q":
        return False


def get_latest_order_ID(orders_sheet):
    latest_order_ID = orders_sheet.col_values(1)[-1]
    today_date = datetime.today().strftime("%Y%m%d")
    
    if today_date not in latest_order_ID:
        last_orderID = 0
    else:
        last_orderID= int(latest_order_ID[-4:])
        
    return last_orderID

def prepare_new_order():
    
    orders_sheet = connect_google_sheets('orders')        
    last_orderID = get_latest_order_ID(orders_sheet)

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
            order_comfirmed, total_sum= summary_order_confirm(pizza_list)
            
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
    print("\nSelect the order item(s) you wish to remove (inputs can be comma-separated integers)")
    print(input_list)
    for ind, order in enumerate(input_list):
        description_str, price_str = order.summary()
        print(f"{ind+1}) {description_str:<70}| {price_str}")
    remove_items= input("Enter your choice: \n")
    
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
                raise ValueError(f"'{value}' is not an integer")
            value = int(value)
            
            # 5 check if within range
            if value < min_value or value>max_value:
                raise ValueError(f"Value '{value}' is out of range. The input values must be between {min_value} and {max_value}")

    except ValueError as e:
        print(f"\nInvalid entry: {e}, please try again.\n")
        return False

    return True
        


def main():
    """
    Run the application to initiate requests for user input
    """    
    continue_app=True
    while continue_app:

        order = prepare_new_order()
        continue_app= update_orders_sheet(order)

main()

    