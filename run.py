import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

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
    "1": "mushrooms",
    "2": "mixed peppers",
    "3": "jalapenos",
    "4": "cheese",
    "5": "pepperoni",
    "6": "chicken",
    "7": "beef",
    "8": "bacon",
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

def main():

    print("Main is running")
    
    # orders_sheet = connect_google_sheets('orders')
    # orders_df = get_as_dataframe(orders_sheet)
    # print(orders_df)

# main()

#### Pizza type
for key, value in PIZZA_MENU.items():
    # value['label']
    print(f"{key}) {value['name']:<20}  | {value['base_toppings']}")

ind = input("Choose your pizza type: \n")
print(f"User chose: \n{PIZZA_MENU[ind]['name']}")

#### Pizza size
for key, value in PIZZA_SIZES.items():
    # value['label']
    print(f"{key}) {value['label']:<20}  | £{value['price']}")

ind = input("Choose your pizza size: \n")
print(f"User chose: \n{PIZZA_SIZES[ind]['label']}")


#### pizza extra toppings
for key, value in EXTRA_TOPPINGS.items():
    # value['label']
    print(f"{key}) {value:<20}")

ind = input("any extra toppingas?: \n")
print(f"User chose: \n{EXTRA_TOPPINGS[ind]}")
