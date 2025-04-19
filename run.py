import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
from collections import Counter


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


def connect_google_sheets(sheet_name):
    
    CREDS = Credentials.from_service_account_file('creds.json')
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    SHEET = GSPREAD_CLIENT.open('fresh_leafy_greens')
    
    sheet_object = SHEET.worksheet(sheet_name)
    
    return sheet_object

def get_user_inputs():
    #### Pizza type
    for key, value in PIZZA_MENU.items():
        print(f"{key}) {value['name']:<20}  | {value['base_toppings']}")

    pizza_ind = input("Choose your pizza type: \n")
    pizza_type = PIZZA_MENU[pizza_ind]['name']

    #### Pizza size
    for key, value in PIZZA_SIZES.items():
        print(f"{key}) {value['label']:<20}  | £{value['price']}")

    size_ind = input("Choose your pizza size: \n")
    pizza_size = PIZZA_SIZES[size_ind]['label']

    #### pizza extra toppings
    for key, value in EXTRA_TOPPINGS.items():
        print(f"{key}) {value:<20}")

    toppings_ind_list = input("any extra toppingas?: \n")
    toppings_items = [EXTRA_TOPPINGS[x] for x in  toppings_ind_list.split(",")]
    pizza_toppings = [f"{count} x {item}" for item, count in Counter(toppings_items).items()]

    print(pizza_toppings)
    

def main():

    print("Main is running")
    
    # orders_sheet = connect_google_sheets('orders')
    # orders_df = get_as_dataframe(orders_sheet)
    # print(orders_df)

# main()
get_user_inputs()


