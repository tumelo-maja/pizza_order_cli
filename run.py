import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
from collections import Counter
from datetime import datetime



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

EXTRA_TOPPING_PRICE = 1.25

PIZZA_SIZES = {
    "1": {
        "label": 'Small - 9" (23 cm)',
        "size_inch": '9"',
        "size_cm": '23 cm',
        "price": 8.99
    },
    "2": {
        "label": 'Medium - 12" (30 cm)',
        "size_inch": '12"',
        "size_cm": '30 cm',
        "price": 10.99
    },
    "3": {
        "label": 'Large - 15" (38 cm)',
        "size_inch": '15"',
        "size_cm": '38 cm',
        "price": 14.99
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
    
    def total_price(self):
        
        base_toppings_total= self.base_price + (len(self.base_toppings)*EXTRA_TOPPING_PRICE)
        
        return round(base_toppings_total)

class Order():
    """
    Creates an instance order.
    """
    def __init__(self, pizza):
        self.pizza = pizza
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.order_number = self.create_order_number()

    def total_price(self):
        total = self.pizza.total_price()
        return round(total, 2)

    def summary(self):
       
        return {
            "Order Number": self.order_number,
            "Date": self.date,
            "Pizza Name": self.pizza.name,
            "Pizza Size": self.pizza.size,
            "Toppings": self.pizza.extra_toppings,
            "Total": self.total_price(),
            "Status": "Ready",
        }
    
    def create_order_number(self):
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

def get_user_inputs():
    """
    Get input from user for the pizza order options

    Returns
    -------
    None.

    """
         
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
    
    return pizza_object

def choose_pizza_name(PIZZA_MENU):
    print("Choose your Pizza:\n")
    for key, value in PIZZA_MENU.items():
        print(f"{key}) {value['name']:<20}  | {', '.join(value['base_toppings'])}")
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
    print("Any extra toppings? (separated by comma): \n")
    for key, value in EXTRA_TOPPINGS.items():
        print(f"{key}) {value:<20}")
    toppings_ind_list = input("Enter your choice(s): \n")
    toppings_items = [EXTRA_TOPPINGS[x] for x in  toppings_ind_list.split(",")]

    pizza_toppings = {'labels': [f"{count} x {item}" for item, count in Counter(toppings_items).items()], 
                      'Counts': len(toppings_items)}
    
    return pizza_toppings

def print_pizza_summary(pizza_size, pizza_name, pizza_toppings):
    print("Order summary: \n")
    summary_str=f"1) {pizza_size} {pizza_name} pizza with "
    if pizza_toppings['labels']:
        print(summary_str + "the following extra toppings:")
        print(" " + "\n ".join(pizza_toppings['labels']))
    else:
        print(summary_str + "no extra toppings")
    


def main():
    """
    Run the application to initiate requests for user input
    """

    print("Main is running")
    
    # orders_sheet = connect_google_sheets('orders')
    # orders_df = get_as_dataframe(orders_sheet)
    # print(orders_df)
    user_pizza = get_user_inputs()
    # print(user_pizza.name)
    # print(user_pizza.base_toppings)
    # print(user_pizza.size)
    



main()


