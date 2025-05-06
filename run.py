import gspread
from google.oauth2.service_account import Credentials
from collections import Counter
from datetime import datetime
import pandas as pd
import os
from pizza_meals import Meal, Order
from menu_items import (EXTRA_TOPPINGS,EXTRA_DIP, SIDES_MENU,DRINKS_MENU, EXTRAS_NAMES,PIZZA_MENU,PIZZA_SIZES)

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

ORDER_NUMBER_LENGTH =12
DATETIME_FORMAT ="%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_ORDER="%Y%m%d"

def connect_google_sheets(sheet_name):
    """
    Setup and connects API to the google sheet and links the input 'sheet_name' using private API key.

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

def create_order(meal_list):
    """
    Creates a list Meal objects built from a sequence of inputs 

    Args:
        meal_list (list): A list to store Meal objects or append to existing objects int the list.

    Returns:
        list: A list of Meal objects
    

    """
    continue_order = True
    while continue_order:
        # choose pizza name
        pizza_name, pizza_base = choose_pizza_name()

        # choose pizza size
        pizza_size, pizza_price = choose_pizza_size()

        # Choose extra toppigns
        pizza_extra_toppings = choose_extra_items('toppings',8)

        # Choose extra dips
        dips = choose_extra_items('Dips',4)
        
        # Choose sides
        sides = choose_extra_items('sides',6)

        # Choose drinks
        drinks = choose_extra_items('drinks',8)
        
        # Meal qunatities
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
            print(color_text("\nWould you like to add another meal?",15))
            print(color_text(f"1) Yes {chr(0x2705)} \n2) No  {chr(0x274C)}",82))
            user_input = strppied_input(color_text("Enter your choice:\n",166))
            if user_input == '99':
               confirm_exit()
               continue
            if validate_single_entry(user_input,1,2):
                break

        if user_input == '2':
            continue_order = False

    return meal_list

def confirm_exit():
    '''
    Displays a warning message showing that returning to main menu mid-order will clear all current order items.

    If the user confirms, the application navigates back to the main menu.

    Returns:
        None
    '''
    print(f"\n{chr(0x26A0)} Returning to the main menu will clear all items in your current order.")
    while True:
        user_input = strppied_input(color_text(f"     Are you sure you want to continue? \n1) Yes {chr(0x2705)} \n2) No  {chr(0x274C)}\n",166))

        if validate_single_entry(user_input,1,2):
            break
    if user_input == "1":
        main_menu()
    #clear_console()

def choose_pizza_name():
    '''
    Displays the list of available pizza options and their base toppings.
    
    It prompts user to select one of the options to proceed. 
    Validates user's input and allows user to return to main menu.

    Returns:
        tuple:
            str: The selected pizza name.
            list: The list of base toppings for the selected pizza.
    '''    
    #clear_console()
    indent_value=18
    while True:
        print(color_text("\nChoose your pizza (one pizza at a time)",15))
        display_return_home_option()
        print(color_text(f"Our pizzas {chr(0x1F355)}".ljust(indent_value) + "| Base toppings",15))
        print(color_text("-"*35,15))
        for key, value in PIZZA_MENU.items():
            print(color_text(f"{key}) {value['name']}".ljust(indent_value),82) + color_text("|",15)+color_text(f" {', '.join(value['base_toppings'])}",82))
            
        user_input = strppied_input(color_text("Enter your choice:\n",166))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_single_entry(user_input,1,5):
            break
    pizza_name = PIZZA_MENU[user_input]['name']
    pizza_base = PIZZA_MENU[user_input]['base_toppings']

    return pizza_name, pizza_base

def choose_pizza_size():
    '''
    Displays the list of available pizza size options and their prices.
    
    It prompts user to select one of the options to proceed. 
    Validates user's input and allows user to return to main menu.

    Returns:
        tuple:
            str: The selected pizza size label.
            float: The price of the selected pizza size.
    '''     
    #clear_console()
    indent_value=21
    while True:
        print(color_text("\nChoose the size of your pizza",15))
        display_return_home_option()        
        print(color_text(f"Pizza size {chr(0x1F355)}".ljust(indent_value) + "| Price (£)",15))
        print(color_text("-"*33,15))
        for key, value in PIZZA_SIZES.items():
            print(color_text(f"{key}) {value['label']} {value['size_inch']}({value['size_cm']})".ljust(indent_value),82) + color_text("|",15)+color_text(f"{price_format(value['price'])}".rjust(7),82))
        user_input = strppied_input(color_text("Enter your choice:\n",166))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_single_entry(user_input,1,3):
            break
    pizza_size = PIZZA_SIZES[user_input]['label']
    pizza_price = PIZZA_SIZES[user_input]['price']

    return pizza_size, pizza_price

def choose_extra_items(item_type,count_max):
    """
    Displays a list of extra items and their prices for a specified item_type.

    It prompts user to select none or more of the options to proceed. Mutliple selection are allowed up to a specified limit i.e. 'count_max'. 
    Validates user's inputs and allows user to return to main menu.

    Args:
        item_type (str): The category of extras to display ('toppings', 'Dips', 'drinks', or 'sides').
        count_max (int): The maximum number of items the user can select for a specified item_type.

    Returns:
        dict: A dictionary containing:
            - 'labels' (list): labels of selected items and their counts.
            - 'item_indx' (list): Indexes and counts of selected for accessing other properties of the item_type menu.
            - 'counts' (int): Total number of selected items.
    """
    #clear_console()
    if item_type=='toppings':
        menu_list = EXTRA_TOPPINGS
        indent_value=18
        row_dashes=32
        item_type = f'extra {item_type}'
    elif item_type=='Dips':
        menu_list = EXTRA_DIP 
        indent_value=22
        row_dashes=36
        item_type = f'extra {item_type}'
    elif item_type=='drinks':
        indent_value=26
        row_dashes=40
        menu_list = DRINKS_MENU
    elif item_type=='sides':
        indent_value=26
        row_dashes=40
        menu_list = SIDES_MENU
        
    
    while True:
        print(color_text(f"\nAny {item_type.lower()}? (You can select up to {count_max} items",15))
        print(color_text("- input(s) can be comma-separated integers",166))
        display_return_home_option()
        print(color_text(f"{item_type.capitalize():^{indent_value}}"+"| Price (£)",15))
        print(color_text("-"*row_dashes,15))

        for key, value in menu_list.items():
            
            item_str = f"{key}) {value.get('icon', ' ')}  {value['name']}"
            if key == "0":
                print(color_text(f"{item_str:<{indent_value}}",82) + color_text("|",15) + color_text("-".center(5),82))
            else:
                print(color_text(f"{item_str:<{indent_value}}",82) + color_text("|",15)+ color_text(f"{price_format(value['price'])}".rjust(5),82))
                
        user_input = strppied_input(color_text("Enter your choice(s):\n",166))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_multiple_entries(user_input,0,len(menu_list)-1,count_max):
            break
        
    extra_items = [menu_list[x]['name'] for x in user_input.split(",") if x != "0"]
    extra_items_indx = [x for x in user_input.split(",") if x != "0"]
  
    extra_items_dict = {'labels': [f"{count} x {item}" if extra_items != ["None"] else None for item, count in Counter(extra_items).items()],
                        'item_indx': [[f"{item}",count] if extra_items != ["None"] else None for item, count in Counter(extra_items_indx).items()],
                      'counts': len(extra_items)}

    return extra_items_dict    
   
def enter_meal_quantity():
    """
    Prompts the user to enter the quantity of a meal they wish to order.

    The function prompts user to an integer between 1 and 50 to proceed. 
    Validates user's inputs and allows user to return to main menu.

    Returns:
        int: The number of meal portions.
    """    
    #clear_console()    
    while True:
        print(color_text("\nHow many qunatities of this meal would you like?",15))
        display_return_home_option()
        user_input = strppied_input(color_text("Enter your required quantity (1-50):\n",166))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_single_entry(user_input,1,50):
            break

    return int(user_input)

def print_meal_summary(meal_object):
    """
    Displays a summary of a meal object showing the name, size, any extras and meal quantity.

    If any of the extras (toppings, dips, sides, drinks) items have been selected, they will be displayed with their quantities.

    Args:
        meal_object (Meal): The Meal object containing all details of the selected meal options.

    Returns:
        None
    """    
    #clear_console()
    print(color_text("\nOrder summary: ",15))
    summary_str = f"{meal_object.quantity} x {meal_object.pizza_size} {meal_object.pizza_name} Pizza with "
    extras =meal_object.extras_summary()
    if len(extras) >0:
        print(color_text(summary_str + "the following extra(s):",15))
        indent_value=3
        
        for extra_full,extra_short in EXTRAS_NAMES:
            extra_counts =getattr(meal_object, extra_full).get('counts')
            extra_label =getattr(meal_object, extra_full).get('labels')
            if extra_counts>0:
        
                if len(extra_label) > 1:
                    align_space = " " * len(f"{extra_short}".ljust(indent_value)) + "  "                    
                    print(color_text(f"{extra_short}".ljust(indent_value) + f": {extra_label[0]}\n{align_space}" + f'\n{align_space}'.join(extra_label[1:]),15))
                else: 
                    print(color_text(f"{extra_short}".ljust(indent_value) + f" {extra_label[0]}",15))
        print_extras_description()

    else:
        print(color_text(summary_str + "no extras",15))
        
def summary_order_confirm(input_list):
    #clear_console()
    if not len(input_list):
        print("\nThere are no items in this order")
        input(color_text(f"- Press any key to Main Menu {chr(0x1F3E0)}\n",166))
        main_menu()

    else:
        indent_value=18
        while True:
            print(color_text("\nConfirm your full order:",15))
            total_sum = display_full_order(input_list)
            print(color_text("\n1) Place order".ljust(indent_value+1)+chr(0x1F6D2),82))
            print(color_text("2) Add more items".ljust(indent_value)+chr(0x2795),82))
            print(color_text("3) Remove items".ljust(indent_value)+chr(0x2796),82))
            print(color_text("99) Main Menu".ljust(indent_value)+chr(0x1F3E0),82))
            user_input = strppied_input(color_text("Enter your choice:\n",166))
            if user_input == '99':
                confirm_exit()
                continue
            if validate_single_entry(user_input,1,3):
                break

    return int(user_input)-1,total_sum


def display_full_order(input_list):

    total_sum = 0
    price_indent=9
    str_indent=62
    print(color_text("Items".center(str_indent)+"| Price (£)",15))
    print(color_text("-"*(str_indent+10),15))

    for ind,order in enumerate(input_list):
        description_str, price_str = order.summary()
        print(color_text(f"{ind+1}) {description_str}".ljust(str_indent),220) +color_text("|",15)+ color_text(f"{price_format(price_str)}".rjust(price_indent),220))
        total_sum += order.total_price
    total_sum = round(total_sum, 2)
    print(color_text('_'*(str_indent+10),15))
    print(color_text(f"Total cost {chr(0x1F4B7)} :".center(str_indent) +"|",15)+ color_text(f"{price_format(total_sum)}".rjust(price_indent),220))
    print_extras_description()
    
    return total_sum

def price_format(value):
    return '{:,.2f}'.format(value)

def print_order_summary(order_dict):
    print(color_text("Here's your order summary:\n",15))

    new_labels = ['Order ID','Time','Items','Ready time','Status','Total']
    
    indent_value= 12
    
    for label,value in zip(new_labels,order_dict):
        
        if label== 'Total':
            value = value if isinstance(value, str) else f"£ {price_format(value)}"
            
        if 'time' in label:
            print(color_text("Date".ljust(indent_value) + f"| {value.split(' ')[0]}",15))
            value = value.split(' ')[1][:-3]
        
        if label =='Items' and ',' in value:
            align_space = " " * len(f"{label}".ljust(indent_value)) + color_text("|",15)
            split_str = [color_text(x,220) for x in value.split(',')]
            
            print(color_text(f"{label}".ljust(indent_value) + "|",15)+f" {split_str[0]}\n{align_space}" + f'\n{align_space}'.join(split_str[1:]))

        elif label =='Items': 
            print(color_text(f"{label}".ljust(indent_value) + "|",15) +color_text(f" {value}",220)) 
        elif label =='Status': 
            if value != 'Ready':
                print(color_text(f"{label}".ljust(indent_value) + "|",15) +f" {chr(0x231B)}"+color_text(f"  {value}",166))
            else:
                print(color_text(f"{label}".ljust(indent_value) + "|",15) +f" {chr(0x2705)}"+color_text(f"  {value}",82))
                
        else: 
            print(color_text(f"{label}".ljust(indent_value) + "|" +f" {value}",15))
            
def print_extras_description():
    extras_description = " - ".join(f"{short}: {full.capitalize()}" for full, short in EXTRAS_NAMES)
    print(color_text(f'\n * {extras_description}',166))

def update_orders_sheet(order):
    #clear_console()
    print(color_text("Updating 'order' worksheet...",220))
    order_list_item = list(order.summary.values())
    
    ORDERS_SHEET.append_row(order_list_item)

    print(color_text("'orders' worksheet updated successfully.",220))
    print(color_text(f"\nSuccess!{chr(0x2705)}  {chr(0x1F4AF)}  {chr(0x1F603)}  Thank you for sending your order. It is now being prepared...",220))
    print_order_summary(order.summary.values())
 
    input(color_text(f"\n- Press any key to return to the main menu {chr(0x1F3E0)}\n",166))
    main_menu()

def get_latest_order_ID():
    latest_order_ID = ORDERS_SHEET.col_values(1)[-1]
    today_date = datetime.today().strftime(DATETIME_FORMAT_ORDER)
    
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
            continue_loop, total_price= summary_order_confirm(meal_list)
        elif continue_loop == 2:
            meal_list = remove_order_items(meal_list)
            continue_loop, total_price= summary_order_confirm(meal_list)

    order = Order(meal_list, total_price, last_orderID)
    return order

def remove_order_items(input_list):
    #clear_console()
    while True:
        print(color_text("\nSelect the order item(s) you wish to remove \n(inputs can be comma-separated integers)",15))
        print(color_text("-  enter 0 for no changes",166))
        display_return_home_option()
        display_full_order(input_list)
        user_input = strppied_input(color_text("Enter your choice:\n",166))
        if user_input == '99':
            confirm_exit()
            continue
        if user_input == '0':
            return input_list
            
        if validate_multiple_entries(user_input,1,len(input_list)):
            break
        
    removed_indexes = [int(x)-1 for x in user_input.split(",")]
    
    new_list = [order for i, order in enumerate(input_list) if i not in removed_indexes]
    
    return new_list   

def validate_single_entry(value, min_value=None, max_value=None):
    
    try:
        
        # Check if there are leading zerpos
        if len(value)> 1 and value.startswith("0"):
                raise ValueError(f"'{value}' is not a valid entry. Leading zeros are not allowed")
        
        # Check if input is integer type 
        if not value.isdigit():
            raise ValueError(f"'{value}' is not an integer")
        value = int(value)
        
        # check if input is within range
        if value < min_value or value>max_value:
            raise ValueError(f"Value '{value}' is out of range. The input value must be between {min_value} and {max_value}")

    except ValueError as e:
        print(color_text(f"\n{chr(0x274C)}  Invalid entry: {e}, please try again.",196))
        return False

    return True
        
def validate_multiple_entries(values_input, min_value=None, max_value=None,count_max=None):
    
    try:
        values = [x for x in values_input.split(",")]
        
        #  Check if zero in selected with other options
        if len(values)> 1 and '0' in values:
                raise ValueError(f"'{values_input}' is not a valid entry. You cannot select '0' with any other values")

        # Check number of inputs does not exceed limit
        if count_max is not None and len(values) > count_max:
            raise ValueError(f"You've entered {len(values)} items, you may only add up to {count_max} items")

        for value in values:
            
            # Check if input elements have leading zeros
            if len(value)> 1 and value.startswith("0"):
                    raise ValueError(f"'{value}' is not a valid entry. Leading zeros are not allowed")
            
            # Check if input strictly has integer type only
            if not value.isdigit():
                raise ValueError(f"'{value}' is not an integer. The input values must be integers between {min_value} and {max_value}")
            value = int(value)
            
            # check if input is within range
            if value < min_value or value>max_value:
                raise ValueError(f"Value '{value}' is out of range. The input values must be integers between {min_value} and {max_value}")

    except ValueError as e:
        print(color_text(f"\n{chr(0x274C)}  Invalid entry: {e}, please try again.",196))
        return False

    return True

def welcome_page():
    '''
    Displays the welcome screen for the CLI and prompts user to select an action to initiate.

    Returns:
        str: The user's input selection, can be of either of these options (1 - start an order or 2 - track an existing order).
    '''
    # #clear_console()
    dashes = "-"*21
    dashes_slogan= "-"*18
    string_len = 75
    welcome_str = f"{color_text('/'+dashes,166)}{chr(0x1F355)}  {color_text('Welcome to PizzaPalace CLI!',82)} {chr(0x1F355)}{color_text(dashes+'-\\',166)}"
    second_line_str = f"{color_text('|'+dashes_slogan,166)}{color_text(chr(0x1F336),196)*2}  {color_text('Packed with incredible',82)} {color_text('flavors!',196)} {chr(0x1F525)*2}{color_text(dashes_slogan+'-|',166)}"
    print(color_text(" "+ "_"*string_len,166))
    print(welcome_str)
    print(color_text("|"+"-"*string_len +"|",166))
    print(second_line_str) 
    print(color_text("\\"+"_"*string_len +"/",166))
    indent_value =21
    
    while True:
        print(color_text(f"\nWhat would you like to do today? {chr(0x1F600)}",15))
        print(color_text("1) Place an order".ljust(indent_value) + chr(0x1F4DD),82))
        print(color_text("2) Track an order".ljust(indent_value) + chr(0x1F50D),82))

        task_to_do = strppied_input(color_text("Enter your choice:\n",166))
        if validate_single_entry(task_to_do,1,2):
            break
    return task_to_do        

def track_order():
    #clear_console()
    while True:
        print(color_text("Track order:",15))
        display_return_home_option()
        user_input = strppied_input(color_text(f"Enter your {ORDER_NUMBER_LENGTH}-digit order number:\n",166))
        if user_input== '99':
            main_menu()
            break
        elif not validate_order_number(user_input):
            continue
        
        order_number= int(user_input)
        update_orders_status()
        orders_df = pd.DataFrame(ORDERS_SHEET.get_all_records())
        order_index = orders_df[orders_df['Order ID'] == order_number].index
        
        if not len(order_index):
            print(color_text(f"\n{chr(0x274C)} Order number {order_number} not found. Please check the number and try again.\n",196))

            continue
            
        order_dict = orders_df.iloc[order_index[0]].to_dict()
        status_str, order_dict = check_order_status(order_dict)     
    
        print_order_summary(order_dict.values())
        print(f"\n{status_str}")
        indent_value=23
        while True:
            print(color_text("\n1) Track another order ".ljust(indent_value) + chr(0x1F50D),82))
            print(color_text("99) Main Menu".ljust(indent_value)+chr(0x1F3E0),82))
            user_input = strppied_input(color_text("Enter your choice:\n",166))
            if user_input == '99':
                main_menu()
                break
            if validate_single_entry(user_input,1,1):
                break
            
        if user_input=='1':
            #clear_console()
            continue
    
def update_orders_status():
    print(color_text("Updating order status...",220))
    orders_df = pd.DataFrame(ORDERS_SHEET.get_all_records())
    
    for ind, row in orders_df.iterrows():
        status_value = row['Order ready time']
        
        if status_value != 'Ready':
            
            current_time = datetime.now()
            ready_time = datetime.strptime(status_value,DATETIME_FORMAT)
            
            time_difference =int((current_time -ready_time).total_seconds())
            
            if time_difference > 0:
                orders_df.at[ind, 'Order status'] = 'Ready'
            else:
                orders_df.at[ind, 'Order status'] = 'Preparing'

                
    status_values = [[status_str] for status_str in orders_df['Order status'].tolist()]
    ORDERS_SHEET.update(values=status_values,range_name=f'E2:E{len(status_values)+1}')

def check_order_status(order_dict):
    print(color_text("Checking your order status...",220))
    
    order_ready_datetime = datetime.strptime(order_dict['Order ready time'], DATETIME_FORMAT)
    current_time = datetime.now()
    time_difference =int((current_time -order_ready_datetime).total_seconds() )
    
    order_ready_datestr=order_ready_datetime.strftime(DATETIME_FORMAT)[:-3]
        
    if time_difference >0:
        status_str = color_text(f"Your order has been ready since {order_ready_datestr}",82)
    elif time_difference <0:
        status_str = color_text(f"Your order will be ready at {order_ready_datestr}",166)
    else:
        status_str = color_text("Your order is ready now",82)
    
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
        print(color_text(f"\n{chr(0x274C)}  Invalid entry: {e}, please try again.\n",196))
        return False

    return True

def strppied_input(message):
    return input(message).replace(' ', '')

def display_return_home_option():
    print(color_text("- enter 99 to return to the main menu\n",166))

def color_text(message,color_code):

    return f"\033[38;5;{color_code}m{message}\033[0m"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    """
    Run the application to initiate requests for user input
    """    

    continue_app=True
    while continue_app:
        
        user_choice = welcome_page()
        
        if user_choice == "1":
            
            last_orderID = get_latest_order_ID()
            order = prepare_new_order(last_orderID)
    
            update_orders_sheet(order)
        elif user_choice == "2":
            track_order()

ORDERS_SHEET = connect_google_sheets('orders')        

main_menu()





    