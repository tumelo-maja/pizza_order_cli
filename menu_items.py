"""
Menu options and pricing
for pizzas and extras (dips, sides, and drinks).

Dictionaries included in this file:
- PIZZA_MENU: 5 x Available pizza options, each with custom base toppings.
- PIZZA_SIZES: 3 x Size options with price.
- EXTRA_TOPPINGS: 8 x Optional extra toppings, their prices and emoji icons.
- EXTRA_DIP: 4 x Optional extra dips, their prices and emoji icons.
- SIDES_MENU: 3 x Optional sides, their prices
            and emoji icons for chicken wings and fries.
- DRINKS_MENU: 8 x Optional drinks, their prices and emoji icons.
- EXTRAS_NAMES: Tuple of shorthand and full display labels for extras.
"""

PIZZA_MENU = {
    "1": {"name": "Hawaiian",
          "base_toppings": ["ham", "pineapple", "cheese"]},
    "2": {"name": "Pepperoni",
          "base_toppings": ["pepperoni", "cheese", "tomato sauce"]},
    "3": {"name": "Vegetarian",
          "base_toppings": ["mushrooms", "peppers", "onions", "olives"]},
    "4": {"name": "All Meaty",
          "base_toppings": ["pepperoni", "sausage", "ham", "olives", "beef"]},
    "5": {"name": "Spicy Chicken",
          "base_toppings": ["spicy chicken", "jalapenos", "onions", "cheese"]},
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

DRINKS_MENU = {
    "0": {"name": "None", 'icon': chr(0x274C)},
    "1": {"name": "Coke Zero 330ml", "price": 1.20, 'icon': chr(0x1F964)},
    "2": {"name": "Coke 330ml", "price": 1.30, 'icon': chr(0x1F964)},
    "3": {"name": "Sprite 330ml", "price": 1.30, 'icon': chr(0x1F964)},
    "4": {"name": "Pepsi 330ml", "price": 1.20, 'icon': chr(0x1F964)},
    "5": {"name": "Apple Juice 330ml", "price": 1.50, 'icon': chr(0x1F9C3)},
    "6": {"name": "Mango Juice 330ml", "price": 1.50, 'icon': chr(0x1F9C3)},
    "7": {"name": "Orange Juice 330ml", "price": 1.50, 'icon': chr(0x1F9C3)},
    "8": {"name": "Still Water 500ml", "price": 1.00, 'icon': chr(0x1F4A7)},
}

EXTRA_TOPPING_PRICE = 1.50
EXTRA_TOPPINGS = {
    "0": {"name": "None", 'icon': chr(0x274C)},
    "1": {"name": "Mushrooms",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1F344)},
    "2": {"name": "Pineapple",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1F34D)},
    "3": {"name": "Jalapenos",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1F336)},
    "4": {"name": "Cheese",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1F9C0)},
    "5": {"name": "Olives",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1FAD2)},
    "6": {"name": "Chicken",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1F357)},
    "7": {"name": "Beef",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1F969)},
    "8": {"name": "Sweet Corn",
          "price": EXTRA_TOPPING_PRICE, 'icon': chr(0x1F33D)},
}

EXTRA_DIP_PRICE = 0.60
EXTRA_DIP = {
    "0": {"name": "None", 'icon': chr(0x274C) + "\u00A0"},
    "1": {"name": "Garlic & Herb",
          "price": EXTRA_DIP_PRICE, 'icon': chr(0x1F9C4)},
    "2": {"name": "BBQ",
          "price": EXTRA_DIP_PRICE, 'icon': chr(0x1F356)},
    "3": {"name": "Sriracha",
          "price": EXTRA_DIP_PRICE, 'icon': chr(0x1F336)},
    "4": {"name": "Ranch",
          "price": EXTRA_DIP_PRICE, 'icon': chr(0x1F95B)},
}

SIDES_PRICE = 1.50
SIDES_MENU = {
    "0": {"name": "None", 'icon': chr(0x274C)},
    "1": {"name": "Small Fries", "price": 1.80, 'icon': chr(0x1F35F)},
    "2": {"name": "Medium Fries", "price": 2.30, 'icon': chr(0x1F35F)},
    "3": {"name": "Large Fries", "price": 2.80, 'icon': chr(0x1F35F)},
    "4": {"name": "8 x Chicken Wings", "price": 4.50, 'icon': chr(0x1F357)},
    "5": {"name": "12 x Chicken Wings", "price": 6.50, 'icon': chr(0x1F357)},
    "6": {"name": "16 x Chicken Wings", "price": 8.00, 'icon': chr(0x1F357)},
}

EXTRAS_NAMES = (('toppings', 'TPs'), ('dips', 'DPs'),
                ('sides', 'SDs'), ('drinks', 'DKs'))
