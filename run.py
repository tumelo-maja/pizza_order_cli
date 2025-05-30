import gspread
from google.oauth2.service_account import Credentials
from collections import Counter
from datetime import datetime
import pandas as pd
import os
import re
from pytz import timezone
from pizza_meals import Meal, Order
from menu_items import (
    EXTRA_TOPPINGS,
    EXTRA_DIP,
    SIDES_MENU,
    DRINKS_MENU,
    EXTRAS_NAMES,
    PIZZA_MENU,
    PIZZA_SIZES)

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

ORDER_NUMBER_LENGTH = 12
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_ORDER = "%Y%m%d"
UK_TIMEZONE = timezone('Europe/London')

ORANGE = 166
WHITE = 15
GREEN = 82
YELLOW = 220


def connect_google_sheets(sheet_name):
    """
    Setup and connects API to the google sheet,
      and links the input 'sheet_name' using private API key.

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


def create_meal(meal_list):
    """
    Creates a list of Meal objects built from a sequence of inputs

    Args:
        meal_list (list): A list to store Meal objects  or append
                          to existing objects int the list.

    Returns:
        list: A list of Meal objects


    """
    continue_order = True
    while continue_order:
        # choose pizza name
        pizza_name, pizza_base = choose_pizza_name()

        # choose pizza size
        pizza_size, pizza_price = choose_pizza_size()

        # Choose extra toppings
        pizza_extra_toppings = choose_extra_items('toppings', 8)

        # Choose extra dips
        dips = choose_extra_items('Dips', 4)

        # Choose sides
        sides = choose_extra_items('sides', 6)

        # Choose drinks
        drinks = choose_extra_items('drinks', 8)

        # Meal quantities
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

        print_meal_summary(meal_object)

        meal_list.append(meal_object)

        while True:
            print(color_text("\n Would you like to add another meal?", WHITE))
            display_return_home_option()
            print(INDENT_ALL + color_text(
                f"1) Yes {chr(0x2705)} \n 2) No  {chr(0x274C)}", GREEN))
            user_input = strip_input(
                color_text("Enter your choice:", ORANGE))
            if user_input == '99':
                confirm_exit()
                continue
            if validate_single_entry(user_input, 1, 2):
                break
        user_input = int(user_input)
        if user_input == 2:
            continue_order = False

    return meal_list


def confirm_exit():
    '''
    Displays a warning message showing that returning to main menu
    mid-order will clear all current order items.

    If the user confirms, the application navigates back to the main menu.

    Returns:
        None
    '''
    print(INDENT_ALL + f"\n{color_text(chr(0x26A0),YELLOW)} Returning to the "
          "main menu will clear all items in your current order.")
    while True:
        user_input = strip_input(color_text(
            f"     Are you sure you want to continue? "
            f"\n1) Yes {chr(0x2705)} \n2) No  {chr(0x274C)}\n", ORANGE))

        if validate_single_entry(user_input, 1, 2):
            break
    user_input = int(user_input)
    if user_input == 1:
        main_menu()
    clear_console()


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
    clear_console()
    indent = 18
    while True:
        print(color_text("\n Choose your pizza (one pizza at a time)", WHITE))
        display_return_home_option()
        print(INDENT_ALL + color_text(f"Our pizzas {chr(0x1F355)}".ljust(
            indent) + "| Base toppings", WHITE))
        print(INDENT_ALL + color_text("-"*35, WHITE))
        for key, value in PIZZA_MENU.items():
            print(INDENT_ALL +
                  color_text(f"{key}) {value['name']}".ljust(indent), GREEN) +
                  color_text("|", WHITE) +
                  color_text(f" {', '.join(value['base_toppings'])}", GREEN))

        user_input = strip_input(color_text("Enter your choice:", ORANGE))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_single_entry(user_input, 1, 5):
            break
    user_input = str(int(user_input))
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
    clear_console()
    indent = 21
    while True:
        print(color_text("\n Choose the size of your pizza", WHITE))
        display_return_home_option()
        print(INDENT_ALL + color_text(f"Pizza size {chr(0x1F355)}".ljust(
            indent) + "| Price (£)", WHITE))
        print(INDENT_ALL + color_text("-"*33, WHITE))
        for key, value in PIZZA_SIZES.items():
            item_str = f"{key}) {value['label']} " + \
                      f"{value['size_inch']}" + \
                      f"({value['size_cm']})"

            print(INDENT_ALL + color_text(item_str.ljust(indent), GREEN) +
                  color_text("|", WHITE) +
                  color_text(f"{price_format(value['price'])}".rjust(7),
                             GREEN))
        user_input = strip_input(color_text("Enter your choice:", ORANGE))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_single_entry(user_input, 1, 3):
            break
    user_input = str(int(user_input))
    pizza_size = PIZZA_SIZES[user_input]['label']
    pizza_price = PIZZA_SIZES[user_input]['price']

    return pizza_size, pizza_price


def choose_extra_items(item_type, count_max):
    """
    Displays a list of extra items and their prices for a specified item_type.

    It prompts user to select none or more of the options to proceed.
    Multiple selection are allowed up to a specified limit i.e. 'count_max'.
    Validates user's inputs and allows user to return to main menu.

    Args:
        item_type (str): The category of extras to display
                        ('toppings', 'Dips', 'drinks', or 'sides').
        count_max (int): The maximum number of items the user can
                        select for a specified item_type.

    Returns:
        dict: A dictionary containing:
            - 'labels' (list): labels of selected items and their counts.
            - 'item_index' (list): Indexes and counts of selected for
                    accessing other properties of the item_type menu.
            - 'counts' (int): Total number of selected items.
    """
    clear_console()
    if item_type == 'toppings':
        menu_list = EXTRA_TOPPINGS
        indent = 18
        row_dashes = 32
        item_type = f'extra {item_type}'
    elif item_type == 'Dips':
        menu_list = EXTRA_DIP
        indent = 22
        row_dashes = 36
        item_type = f'extra {item_type}'
    elif item_type == 'drinks':
        indent = 26
        row_dashes = 40
        menu_list = DRINKS_MENU
    elif item_type == 'sides':
        indent = 26
        row_dashes = 40
        menu_list = SIDES_MENU

    while True:
        print(color_text(
            f"\n Any {item_type.lower()}? " +
            f"(You can select up to {count_max} items)", WHITE))
        print(INDENT_ALL +
              color_text("- input(s) can be comma-separated integers", ORANGE))
        display_return_home_option()
        print(INDENT_ALL + color_text(
            f"{item_type.capitalize():^{indent}}"+"| Price (£)", WHITE))
        print(INDENT_ALL + color_text("-"*row_dashes, WHITE))

        for key, value in menu_list.items():

            item_str = f"{key}) {value.get('icon', ' ')}  {value['name']}"
            if key == "0":
                print(INDENT_ALL + color_text(f"{item_str:<{indent}}", GREEN) +
                      color_text("|", WHITE) +
                      color_text("-".center(5), GREEN))
            else:
                print(INDENT_ALL + color_text(f"{item_str:<{indent}}", GREEN) +
                      color_text("|", WHITE) +
                      color_text(f"{price_format(value['price'])}".rjust(5),
                                 GREEN))

        user_input = strip_input(color_text("Enter your choice(s):",
                                               ORANGE))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_multiple_entries(
            user_input, 0,
            len(menu_list)-1,
            count_max
        ):
            break

    extra_items_index = [str(int(x)) for x in user_input.split(",") if x != "0"]
    extra_items = [menu_list[x]['name'] for x in extra_items_index if x != "0"]

    extra_items_dict = {'labels': [f"{count} x {item}"
                                   if extra_items != ["None"]else None
                                   for item, count in
                                   Counter(extra_items).items()],
                        'item_index': [[f"{item}", count]
                                      if extra_items != ["None"] else None
                                      for item, count in
                                      Counter(extra_items_index).items()],
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
    clear_console()
    while True:
        print(color_text(
            "\n How many quantities of this meal would you like?", WHITE))
        display_return_home_option()
        user_input = strip_input(color_text(
            "Enter your required quantity (1-50):", ORANGE))
        if user_input == '99':
            confirm_exit()
            continue
        if validate_single_entry(user_input, 1, 50):
            break

    return int(user_input)


def print_meal_summary(meal_object):
    """
    Displays a summary of a meal object showing
    the name, size, any extras and meal quantity.

    If any of the extras (toppings, dips, sides, drinks) items
    have been selected, they will be displayed with their quantities.

    Args:
        meal_object (Meal): The Meal object containing all
                            details of the selected meal options.

    Returns:
        None
    """
    clear_console()
    print(color_text("\n Meal summary: ", WHITE))
    summary_str = f"{meal_object.quantity} x {meal_object.pizza_size}" + \
                  f" {meal_object.pizza_name} Pizza with "
    extras = meal_object.extras_summary()
    if len(extras) > 0:
        print(INDENT_ALL + color_text(summary_str +
                                      "the following extra(s):", WHITE))
        indent = 3

        for extra_full, extra_short in EXTRAS_NAMES:
            extra_counts = getattr(meal_object, extra_full).get('counts')
            extra_label = getattr(meal_object, extra_full).get('labels')
            if extra_counts > 0:

                if len(extra_label) > 1:
                    align_space = " " * \
                        len(f"{extra_short}".ljust(indent)) + "   "
                    print(INDENT_ALL + color_text(f"{extra_short}".ljust(
                        indent) + f": {extra_label[0]}\n{align_space}" +
                            f'\n{align_space}'.join(extra_label[1:]), WHITE))
                else:
                    print(INDENT_ALL + color_text(f"{extra_short}".ljust(
                        indent) + f" {extra_label[0]}", WHITE))
        print_extras_description()

    else:
        print(INDENT_ALL + color_text(summary_str + "no extras", WHITE))


def summary_order_confirm(input_list):
    """
    Run display_full_order() to display the full order summary and
    prompt the user either submit the order, add more meals,
    remove meals, or return to the main menu.
    All user inputs are validated.

    Args:
        input_list (list): A list of Meal objects that
                          make up the current order.

    Returns:
        tuple:
            int: A flow control value based on user's input;
                 derived as 'user_input'-1
                 (0 = confirm, 1 = add more, 2 = remove items).
            float: The total cost of the order.
    """
    clear_console()
    if not len(input_list):
        print(INDENT_ALL + "\nThere are no items in this order")
        input(color_text(f"- Press Enter to Main Menu {chr(0x1F3E0)}\n",
                         ORANGE))
        main_menu()

    else:
        indent = 18
        while True:
            print(color_text("\n Confirm your full order:", WHITE))
            total_sum = display_full_order(input_list)
            print(color_text("\n 1) Submit order".ljust(
                indent+1)+chr(0x1F6D2), GREEN))
            print(INDENT_ALL + color_text("2) Add more meals".ljust(
                indent)+chr(0x2795), GREEN))
            print(INDENT_ALL + color_text("3) Remove meals".ljust(
                indent)+chr(0x2796), GREEN))
            print(INDENT_ALL + color_text("99) Main Menu".ljust(
                indent)+chr(0x1F3E0), GREEN))

            user_input = strip_input(
                color_text("Enter your choice:", ORANGE))
            if user_input == '99':
                confirm_exit()
                continue
            if validate_single_entry(user_input, 1, 3):
                break
    return int(user_input)-1, total_sum


def display_full_order(input_list):
    """
    Displays the full order summary with all meal
    items and their prices and total cost.

    Each meal item is displayed with its description,
    any extras (if included) and price.
    The total order cost is displayed at the bottom.
    Description of extras abbreviations is shown if
    at least one extra item has been included in any of the meal items.

    Args:
        input_list (list): A list of Meal objects each representing
                    a complete meal and collectively a full order.

    Returns:
        float: The total cost of all meals in the order.
    """
    total_sum = 0
    price_indent = 9
    str_indent = 62
    print(INDENT_ALL + color_text("Items".center(str_indent) +
                                  "| Price (£)", WHITE))
    print(INDENT_ALL + color_text("-"*(str_indent+10), WHITE))
    show_extra_note = False

    for ind, order in enumerate(input_list):
        description_str, price_str = order.summary()
        print(INDENT_ALL + color_text(f"{ind+1})"
              f"{description_str}".ljust(str_indent), YELLOW) +
              color_text("|", WHITE) +
              color_text(
                  f"{price_format(price_str)}".rjust(price_indent), YELLOW))
        total_sum += order.total_price
        if '- *' in description_str:
            show_extra_note = True

    total_sum = round(total_sum, 2)
    print(INDENT_ALL + color_text('_'*(str_indent+10), WHITE))
    print(INDENT_ALL + color_text(f"Total cost {chr(0x1F4B7)} :".center(
        str_indent) + "|", WHITE) +
        color_text(f"{price_format(total_sum)}".rjust(price_indent), YELLOW))

    if show_extra_note:
        print_extras_description()

    return total_sum


def price_format(value):
    """
    Formats a numeric value as a price string with
    two decimal places and comma separators.

    Args:
        value (float or int): The numeric value to format.

    Returns:
        str: The formatted price string.
    """
    return '{:,.2f}'.format(value)


def print_order_summary(order_dict):
    """
    Displays a formatted summary of an order.

    The summary includes the order ID, date and
    time, ordered items, ready time,status, and total cost.
    Each meal items is displayed on a individual row for for readability.

    Args:
        order_dict (iterable): A dictionary containing the order details.

    Returns:
        None
    """
    print(INDENT_ALL + color_text("Here's your order summary:", WHITE))

    new_labels = ['Order ID', 'Order Time', 'Items',
                  'Ready time', 'Status', 'Total']
    indent = 12
    for label, value in zip(new_labels, order_dict):

        if label == 'Total':
            value = value if isinstance(
                value, str) else f"£ {price_format(value)}"

        if 'time' in label:
            print(INDENT_ALL + color_text("Date".ljust(indent) +
                  f"| {value.split(' ')[0]}", WHITE))
            value = value.split(' ')[1][:-3]

        if label == 'Items' and ',' in value:
            align_space = " " * \
                len(f"{label}".ljust(indent)) + color_text("|", WHITE)
            split_str = [color_text(x, YELLOW) for x in value.split(',')]

            print(INDENT_ALL + color_text(f"{label}".ljust(indent) +
                                          "|", WHITE) +
                  f" {split_str[0]}\n {align_space}" +
                  f'\n {align_space}'.join(split_str[1:]))

        elif label == 'Items':
            print(INDENT_ALL + color_text(f"{label}".ljust(indent) +
                  "|", WHITE) + color_text(f" {value}", YELLOW))
        elif label == 'Status':
            if value != 'Ready':
                print(INDENT_ALL + color_text(f"{label}".ljust(
                    indent) + "|", WHITE) +
                    f" {chr(0x231B)}"+color_text(f"  {value}", ORANGE))
            else:
                print(INDENT_ALL + color_text(f"{label}".ljust(
                    indent) + "|", WHITE) +
                    f" {chr(0x2705)}"+color_text(f"  {value}", GREEN))

        else:
            print(INDENT_ALL + color_text(f"{label}".ljust(
                indent) + "|" + f" {value}", WHITE))


def print_extras_description():
    """
    Prints a legend note explaining the
    shorthand labels used for extra items in order summaries.

    The labels are taken from a global
    EXTRAS_NAMES constant and formatted for display.

    Returns:
        None
    """
    extras_description = " - ".join(
        f"{short}: {full.capitalize()}" for full, short in EXTRAS_NAMES)
    print(INDENT_ALL + color_text(f'\n * {extras_description}', ORANGE))


def update_orders_sheet(order):
    """
    Appends a new order to the Google Sheets 'orders'
    worksheet and displays confirmation.

    The function extracts summary data from
    the Order object, appends it to the worksheet,
    prints a success message, runs 'print_order_summary()'
    to shows a summary of the submitted order.
    Prompts user to the main menu by pressing Enter key.

    Args:
        order (Order): The completed order object containing
                    the full order details and total order cost.

    Returns:
        None
    """
    clear_console()
    print(color_text("\n Updating 'order' worksheet...", YELLOW))
    order_list_item = list(order.summary.values())

    ORDERS_SHEET.append_row(order_list_item)

    print(color_text(" 'orders' worksheet updated successfully.", YELLOW))
    print(color_text(
        f"\n Success!{chr(0x2705)}  {chr(0x1F4AF)}  {chr(0x1F603)}"
        "  Thank you for sending your order. "
        "It is now being prepared...", YELLOW))
    print_order_summary(order.summary.values())

    input(color_text(
        f"\n - Press Enter to return to the main menu {chr(0x1F3E0)}\n",
        ORANGE))
    main_menu()


def get_latest_order_ID():
    """
    Retrieves the latest order ID from the
    Google Sheet and extracts the last sequence number for today.

    If no order has been placed today, 0 is returned to start the count.
    Otherwise, the latest order number in the last 4 digits is returned.

    Returns:
        int: The last sequence number used for
            today's orders or 0 if there are no was placed today.
    """
    latest_order_ID = ORDERS_SHEET.col_values(1)[-1]
    today_date = datetime.today().strftime(DATE_FORMAT_ORDER)

    if today_date not in latest_order_ID:
        last_orderID = 0
    else:
        last_orderID = int(latest_order_ID[-4:])

    return last_orderID


def create_new_order(last_orderID):
    """
    Handles adding and modifying meal items and creating an order object.

    This function run create_meal() to build a list of meal items.
    User can review the order summary to add or
    remove items, or confirms the final order.

    Args:
        last_orderID (int): The last used sequence number for today's orders.

    Returns:
        Order: An Order object containing the
             finalized meal list, total price, and order ID.
    """
    meal_list = []
    continue_loop = 1

    while continue_loop:

        if continue_loop == 1:
            meal_list = create_meal(meal_list)
            continue_loop, total_price = summary_order_confirm(meal_list)
        elif continue_loop == 2:
            meal_list = remove_meal_items(meal_list)
            continue_loop, total_price = summary_order_confirm(meal_list)

    order = Order(meal_list, total_price, last_orderID)
    return order


def remove_meal_items(input_list):
    """
    Removes one or more meals from the current order.

    User prompted to enter indexes of
    items to remove from the order.
    The input is validated, and the corresponding
    items are excluded from the returned list.

    Args:
        input_list (list): A list of Meal objects
                    representing the current order.

    Returns:
        list: An updated list of Meal objects with the selected items removed.
    """
    clear_console()
    while True:
        print(color_text(
            "\n Select the meal item(s) you wish to remove "
            "\n (inputs can be comma-separated integers)", WHITE))
        print(INDENT_ALL + color_text("- enter 0 for no changes", ORANGE))
        display_return_home_option()
        display_full_order(input_list)
        user_input = strip_input(color_text("Enter your choice:", ORANGE))
        if user_input == '99':
            confirm_exit()
            continue
        if user_input == '0':
            return input_list

        if validate_multiple_entries(
            user_input, 1,
            len(input_list), len(input_list),
            repeat_allowed=False
        ):
            break

    removed_indexes = [int(x)-1 for x in user_input.split(",")]

    new_list = [order for i, order in enumerate(
        input_list) if i not in removed_indexes]

    return new_list


def validate_single_entry(value, min_value, max_value):
    """
    Validates a single digit input according to specific conditions.

    This function checks that the input:
      - is numeric (no other characters are allowed),
      - is within the allowed range specified,

    If the input is invalid, an error message is displayed.

    Args:
        value (str): The user input to validate.
        min_value (int): The minimum input value.
        max_value (int): The maximum input value.

    Returns:
        bool: True if the input is valid
            (meets the conditions), otherwise False.
    """
    try:

        # Check if input is integer type
        if not value.isdigit():
            raise ValueError(f"'{value}' is not an integer")
        value = int(value)

        # check if input is within range
        if value < min_value or value > max_value:
            raise ValueError(
                f"Value '{value}' is out of range."
                "\n The input value must be between "
                f"{min_value} and {max_value}")

    except ValueError as e:
        print(INDENT_ALL + color_text(
            f"\n {chr(0x274C)}  Invalid entry: {e}, please try again.", 196))
        return False

    return True


def validate_multiple_entries(
        values_input,
        min_value,
        max_value,
        count_max,
        repeat_allowed=True):
    """
    Validates multiple comma-separated inputs against specified conditions.

    This function checks that :
      - input contains numeric characters only,
      - each character in the input lies within the range specified,
      - number of characters do not exceed the count limit
      - values are not repeated, where repetition is prohibited
      - '0' option is not selected with any other options

    If the input is invalid, an error message is displayed.

    Args:
        values_input (str): The raw user input string to validate.
        min_value (int): The minimum allowed value for entries.
        max_value (int): The maximum allowed value for entries.
        count_max (int): The maximum number of items allowed in the input.
        repeat_allowed (bool, optional): Whether repeated values are permitted.
                                        Defaults is True.

    Returns:
        bool: True if all input values are valid, otherwise False.
    """
    try:

        # Check for incorrect delimiters
        invalid_delimiters = re.findall(r'[^a-zA-Z0-9\s,]', values_input)
        invalid_del_str = ', '.join([f"'{x}'" for x in invalid_delimiters])
        if len(invalid_delimiters):
            raise ValueError(
                f"'{values_input}' is not a valid entry."
                f"\n{invalid_del_str} delimiter(s) not allowed. "
                "Use comma ',' to separate the values")

        values = [x for x in values_input.split(",")]

        #  Check if zero in selected with other options
        if len(values) > 1 and '0' in values:
            raise ValueError(
                f"'{values_input}' is not a valid entry."
                "\n You cannot select '0' with any other values")

        # Check number of inputs does not exceed limit
        if count_max is not None and len(values) > count_max:
            raise ValueError(
                f"You've entered {len(values)} items,"
                f"\n you may only enter up to {count_max} items")

        # Check for repeated numbers
        if not repeat_allowed:
            if len(values) != len(set(values)):
                raise ValueError(
                    f"'{values_input}' is not a valid entry."
                    "\n Duplicate entries are not allowed")

        for value in values:

            #  Check if zero in selected with other options
            if len(value) > 1 and '0' in value:
                raise ValueError(
                    f"'{values_input}' is not a valid entry."
                    "\n You cannot select '0' with any other values")

            # Check if input strictly has integer type only
            if not value.isdigit():
                raise ValueError(
                    f"'{value}' is not an integer."
                    "\n The input values must be integers "
                    f"between {min_value} and {max_value}")
            value = int(value)

            # check if input is within range
            if value < min_value or value > max_value:
                raise ValueError(
                    f"Value '{value}' is out of range."
                    "\n The input values must be integers "
                    f"between {min_value} and {max_value}")

    except ValueError as e:
        print(INDENT_ALL + color_text(
            f"\n {chr(0x274C)}  Invalid entry: {e}, please try again.", 196))
        return False

    return True


def welcome_page():
    """
    Displays the welcome message and main menu options.

    Prompts the user to start an order or track an existing order.
    All user inputs are validated.

    Returns:
        str: A validated user input - '1' to start a new order
            or '2' to track an existing order.

    """
    clear_console()
    dashes = "-"*21
    dashes_slogan = "-"*18
    string_len = 75
    welcome_str = f"{color_text('/'+dashes, ORANGE)}{chr(0x1F355)}  " + \
        f"{color_text('Welcome to PizzaPalace CLI!', GREEN)} " + \
        f"{chr(0x1F355)}{color_text(dashes+'-\\', ORANGE)}"
    second_line_str = f"{color_text('|'+dashes_slogan, ORANGE)}" + \
        f"{color_text(chr(0x1F336), 196)*2}  " + \
        f"{color_text('Packed with incredible', GREEN)} " + \
        f"{color_text('flavors!', 196)} " + \
        f"{chr(0x1F525)*2}{color_text(dashes_slogan+'-|', ORANGE)}"
    print(INDENT_ALL + color_text(" " + "_"*string_len, ORANGE))
    print(INDENT_ALL + welcome_str)
    print(INDENT_ALL + color_text("|"+"-"*string_len + "|", ORANGE))
    print(INDENT_ALL + second_line_str)
    print(INDENT_ALL + color_text("\\"+"_"*string_len + "/", ORANGE))
    indent = 21

    while True:
        print(color_text(
            f"\n What would you like to do today? {chr(0x1F600)}", WHITE))
        print(INDENT_ALL + color_text("1) Start an order".ljust(
            indent) + chr(0x1F4DD), GREEN))
        print(INDENT_ALL + color_text("2) Track an order".ljust(
            indent) + chr(0x1F50D), GREEN))

        user_input = strip_input(color_text("Enter your choice:", ORANGE))
        if validate_single_entry(user_input, 1, 2):
            break
    user_input = str(int(user_input))
    return user_input


def track_order():
    """
    Prompts the user to enter an order number and
    displays the status and details of the order if it exists.

    This function runs validate_order_number() to
    validate order number and update_orders_status()
    to update orders records.
    if order number exists in the google sheets,
    order summary is displayed including the status ('Ready' or 'Preparing').
    After order summary display, the user can
    track another order or return to the main menu.

    Returns:
        None
    """
    clear_console()
    while True:
        print(INDENT_ALL + color_text("Track order:", WHITE))
        display_return_home_option()
        user_input = strip_input(color_text(
            f"Enter your {ORDER_NUMBER_LENGTH}-digit order number:", ORANGE))
        if user_input == '99':
            main_menu()
            break
        elif not validate_order_number(user_input):
            continue

        order_number = int(user_input)
        update_orders_status()
        orders_df = pd.DataFrame(ORDERS_SHEET.get_all_records())
        order_index = orders_df[orders_df['Order ID'] == order_number].index

        if not len(order_index):
            print(INDENT_ALL + color_text(
                f"\n{chr(0x274C)} Order number {order_number} not found. "
                "Please check the number and try again.\n", 196))
            continue

        order_dict = orders_df.iloc[order_index[0]].to_dict()
        status_str = check_order_status(order_dict)

        print_order_summary(order_dict.values())
        print(INDENT_ALL + f"\n{status_str}")
        indent = 23
        while True:
            print(color_text("\n 1) Track another order ".ljust(
                indent) + chr(0x1F50D), GREEN))
            print(INDENT_ALL + color_text("99) Main Menu".ljust(
                indent)+chr(0x1F3E0), GREEN))
            user_input = strip_input(
                color_text("Enter your choice:", ORANGE))
            if user_input == '99':
                main_menu()
                break
            if validate_single_entry(user_input, 1, 1):
                break


def update_orders_status():
    """
    Updates the status of all orders in
    the worksheet based on their ready time.

    This function checks each order's
    'Order ready time' against the current time.
    If the ready time has passed, the status is updated to 'Ready'.

    Returns:
        None
    """
    print(color_text("\n Updating order status...", YELLOW))
    orders_df = pd.DataFrame(ORDERS_SHEET.get_all_records())

    now_tz_aware = datetime.now().astimezone(UK_TIMEZONE)
    now_time_str = now_tz_aware.strftime(DATE_FORMAT)
    now_time_tz = datetime.strptime(now_time_str, DATE_FORMAT)
    now_time = now_time_tz.replace(tzinfo=UK_TIMEZONE)

    for ind, row in orders_df.iterrows():
        status_value = row['Order status']
        status_datetime = row['Order ready time']

        if status_value != 'Ready':

            ready_time_naive = datetime.strptime(status_datetime, DATE_FORMAT)
            ready_time = ready_time_naive.replace(tzinfo=UK_TIMEZONE)
            time_diff = int((now_time - ready_time).total_seconds())

            if time_diff > 0:
                orders_df.at[ind, 'Order status'] = 'Ready'
            else:
                orders_df.at[ind, 'Order status'] = 'Preparing'

    status_values = [[status_str]
                     for status_str in orders_df['Order status'].tolist()]
    ORDERS_SHEET.update(values=status_values,
                        range_name=f'E2:E{len(status_values)+1}')


def check_order_status(order_dict):
    """
    Checks if the order is ready by checking
    if the status column has the value 'Ready'.

    It returns a text indicating whether
    the order is ready or still being prepared.

    Args:
        order_dict (dict): A dictionary containing
                        order information.

    Returns:
        tuple:
            str: A formatted message indicating whether
                the order is ready or still being prepared.
    """
    print(INDENT_ALL + color_text("Checking your order status...", YELLOW))

    order_ready_datestr = order_dict['Order ready time']

    if order_dict['Order status'] == 'Ready':
        status_str = color_text(
            f" Your order has been ready since {order_ready_datestr}", GREEN)
    else:
        status_str = color_text(
            f" Your order will be ready at {order_ready_datestr}", ORANGE)

    return status_str


def validate_order_number(number):
    """
    Validates the format an order number.

    Function checks that the order number:
    - Contains no spaces
    - Starts with '20'
    - Consists of digits only
    - Has exactly 12 characters

    If the input is invalid, an error message is displayed.

    Args:
        number (str): The order number string input by the user.

    Returns:
        bool: True if the order number is valid, False otherwise.
    """
    try:
        # Check if there are any spaces ' '
        if ' ' in number:
            raise ValueError(
                f"'{number}' is not a valid order number."
                "\n Order number must not contain any spaces")

        # Check if there are leading zeros
        if not number.startswith("20"):
            raise ValueError(
                f"'{number}' is not a valid order number."
                "\n Order number must start with '20'")

        # Check if digit
        if not number.isdigit():
            raise ValueError(
                f"'{number}' is not a valid order number."
                "\n Order number must contain integers only")

        # Check number length
        if len(number) != ORDER_NUMBER_LENGTH:
            raise ValueError(
                f"Order number must have exactly 12 integers "
                f"\n - you provided {len(number)} integers")

    except ValueError as e:
        print(INDENT_ALL + color_text(
            f"\n {chr(0x274C)}  Invalid entry: {e}, please try again.\n", 196))
        return False

    return True


def strip_input(message):
    """
    Removes any spaces from the input() response.

    Args:
        message (str): Message displayed to the user.

    Returns:
        str: The input() response without any spaces.
    """
    return input(INDENT_ALL + message + '\n>').replace(' ', '')


def display_return_home_option():
    """
    Displays a message on how to return to the main menu.

    Returns:
        None
    """
    print(INDENT_ALL + color_text("- enter 99 to return to the main menu\n",
                                  ORANGE))


def color_text(message, color_code):
    """
    Styles the given message string by wrapping it in
    ANSI 256-color formatting with the color code specified.

    Args:
        message (str): The text to be colorized.
        color_code (int): The ANSI color code to apply (0-255).

    Returns:
        str: The message string wrapped in ANSI color codes.
    """
    return f"\033[38;5;{color_code}m{message}\033[0m"


def clear_console():
    """
    Clears the terminal screen.

    Returns:
        None
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def main_menu():
    """
    Run the application to initiate requests for user input

    Returns:
        None
    """
    continue_app = True
    while continue_app:

        user_choice = welcome_page()

        if user_choice == "1":

            last_orderID = get_latest_order_ID()
            order = create_new_order(last_orderID)
            update_orders_sheet(order)

        elif user_choice == "2":
            track_order()


ORDERS_SHEET = connect_google_sheets('orders')

INDENT_ALL = ' '
main_menu()
