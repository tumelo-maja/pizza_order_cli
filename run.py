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
    def __init__(self, name,base_toppings, size, base_price, extra_toppings):
        self.name = name
        self.base_toppings = base_toppings
        self.size = size
        self.base_price = base_price
        self.extra_toppings = extra_toppings
    
    def summary(self):
        extra_str = f"with {self.extra_toppings['counts']} extra topping(s) " if self.extra_toppings['counts']>0 else ''
        description_str =f"1 x {self.name} pizza, {self.size} {extra_str}"
        price_str =f"£{'{:.2f}'.format(self.total_price)}"
        return description_str, price_str
    
    @property
    def total_price(self):
        base_toppings_total= self.base_price + (self.extra_toppings['counts']*EXTRA_TOPPING_PRICE)
        return round(base_toppings_total,2)

class Order():
    """
    Creates an instance order.
    """
    def __init__(self, order_list):
        self.order_list = order_list
        # self.order_items = pizza
        # self.order_toppings = pizza
        self.order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.order_ID = self.create_order_ID()
        
    @property
    def order_ready_time(self):
        BASE_PIZZA_PREP_TIME = 15
        DELAY_PIZZA_PREP_TIME =5
        
        preparation_time=0
        for i, order in enumerate(self.order_list):
            
            if i==0:
                preparation_time+=BASE_PIZZA_PREP_TIME
            else:
                preparation_time+=DELAY_PIZZA_PREP_TIME
            
            if order.extra_toppings['counts'] > 5:
                preparation_time+=DELAY_PIZZA_PREP_TIME
        
        ready_by_time = datetime.strptime(self.order_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes = preparation_time)
        
        return ready_by_time.replace(second=0).strftime("%Y-%m-%d %H:%M:%S")
                
    @property
    def order_items(self):
        
        full_order_str=[]
        for order in self.order_list:
            
            size_str = order.size.split(' - ')[0]
            name_str = order.name
            topping_count = order.extra_toppings['counts']
            
            topping_str = f" - extra toppings: {topping_count}" if topping_count>0 else ''
            
            full_order_str.append(f"1 x {size_str} {name_str}{topping_str}")
            
        return ', '.join(full_order_str)
    
    def total_price(self):
        total = self.pizza.total_price()
        return round(total, 2)

    def summary(self):
       
        return {
            "Order Number": self.order_ID,
            "Date": self.date,
            "Pizza Name": self.pizza.name,
            "Pizza Size": self.pizza.size,
            "Toppings": self.pizza.extra_toppings,
            "Total": self.total_price(),
            "Status": "Ready",
        }
    
    def create_order_ID(self):
        # add some code later
        return 12345


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
    SHEET = GSPREAD_CLIENT.open('fresh_leafy_greens')
    
    sheet_object = SHEET.worksheet(sheet_name)
    
    return sheet_object

def create_new_order(pizza_list=[]):
    """
    Creates new pizza order from user's inpusts 

    Returns
    -------
    Pizza object.

    """
    continue_order=True
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
        
        if int(add_more_pizza) ==2:
            continue_order = False

    
    return pizza_list

def choose_pizza_name(PIZZA_MENU):
    print("\nChoose your Pizza (one pizza at a time):\n")
    for key, value in PIZZA_MENU.items():
        print(f"{key}) {value['name']:<13}  | {', '.join(value['base_toppings'])}")
    pizza_ind = input("Enter your choice: \n")
    pizza_name = PIZZA_MENU[pizza_ind]['name']
    pizza_base = PIZZA_MENU[pizza_ind]['base_toppings']
    return pizza_name, pizza_base

def choose_pizza_size(PIZZA_SIZES):
    print("\nChoose the Pizza size:\n")
    for key, value in PIZZA_SIZES.items():
        print(f"{key}) {value['label']:<20}  | £{value['price']}")
    size_ind = input("Enter your choice: \n")
    pizza_size = PIZZA_SIZES[size_ind]['label']
    pizza_price = PIZZA_SIZES[size_ind]['price']
    return pizza_size, pizza_price

def choose_extra_toppings(EXTRA_TOPPINGS):
    print("\nAny extra toppings? (separated by comma): ")
    for key, value in EXTRA_TOPPINGS.items():
        print(f"{key}) {value:<20}")
    toppings_ind_list = input("Enter your choice(s): \n")
    toppings_items = [EXTRA_TOPPINGS[x] for x in  toppings_ind_list.split(",")]

    pizza_toppings = {'labels': [f"{count} x {item}" for item, count in Counter(toppings_items).items()], 
                      'counts': len(toppings_items)}
    
    return pizza_toppings

def print_pizza_summary(pizza_size, pizza_name, pizza_toppings):
    print("\nOrder summary: ")
    summary_str=f"1) {pizza_size} {pizza_name} pizza with "
    if pizza_toppings['labels']:
        print(summary_str + "the following extra toppings:")
        print(" " + "\n ".join(pizza_toppings['labels']))
    else:
        print(summary_str + "no extra toppings")
    
def confirm_order(input_list):
    print("\nConfirm your full order:")
    total_sum=0
    for order in input_list:
        description_str, price_str = order.summary()
        print(f"{description_str:<70}| {price_str}")
        total_sum+= order.total_price
    total_sum= round(total_sum,2)
    print('-'*78)
    print("Total cost:".ljust(70) + f"| £{'{:.2f}'.format(total_sum)}")
    print("\n1) Place order \n2) Add more items \n3) Remove items")
    order_comfirmed = input("Enter your choice: \n")
    
    if order_comfirmed== "1":
        order_placed(input_list)
    elif order_comfirmed== "2":
        print("You're adding more")
    elif order_comfirmed== "3":
        print("You're removing items")
    else:
        print("Invalid answer")
    
def order_placed(input_list):
    print("Thank you for sending your order")
    print("Your order will be ready at 14:30")
    print("Order number: 1234")
    print("\n1) return to home page")
    print(input_list)
    

def main():
    """
    Run the application to initiate requests for user input
    """

    print("Main is running")
    
    # orders_sheet = connect_google_sheets('orders')
    # orders_df = get_as_dataframe(orders_sheet)
    # print(orders_df)
    pizza_list = create_new_order()
    print("New order created!")
    confirm_order(pizza_list)
    
    myOrder = Order(pizza_list)
    # update_orders_sheet(pizza_list)
    # print(user_pizza.name)
    # print(user_pizza.base_toppings)
    # print(user_pizza.size)
    
    return myOrder
    



myOrder = main()


