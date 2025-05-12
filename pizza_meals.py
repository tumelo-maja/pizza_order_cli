from datetime import datetime, timedelta
from pytz import timezone
from menu_items import (EXTRA_TOPPINGS,
                        EXTRA_DIP,
                        SIDES_MENU,
                        DRINKS_MENU,
                        EXTRAS_NAMES)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_ORDER = "%Y%m%d"
ORDER_NUMBER_LENGTH = 12
UK_TZONE = timezone('Europe/London')


class Meal():
    """
    Represents a meal consisting of a pizza and
        optional extras like toppings, dips, sides, and drinks.

    Attributes:
        pizza_name (str): Name of the pizza.
        pizza_base_toppings (list): base toppings for the pizza.
        pizza_size (str): Size of the pizza.
        pizza_price (float): Base price of the pizza without extras.
        toppings (dict): Selected extra toppings.
        dips (dict): Selected dips.
        sides (dict): Selected side items.
        drinks (dict): Selected drinks.
        quantity (int): Specified number of portions for the meal.
        total_price(float): Total sum of all meal items and quantities
    """

    def __init__(
            self,
            pizza_name,
            pizza_base_toppings,
            pizza_size,
            pizza_price,
            toppings,
            dips,
            sides,
            drinks,
            quantity):
        """
        Creates a Meal instance with pizza and selected extras.
        """
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
        """
        Formats the meal information including extras and
            pizza details into a formatted string.

        Returns:
            tuple: (str, float) containing the formatted
                  meal description and total price.
        """
        description_str = f"{self.quantity} x {self.pizza_name} " + \
            f"{self.pizza_size} {chr(0x1F355)} {self.extras_summary()}"

        return description_str, self.total_price

    @property
    def total_price(self):
        """
        Calculates the total cost of all meal items including quantities.

        Returns:
            float: Meal total cost.
        """
        toppings_prices = [EXTRA_TOPPINGS[x[0]]['price']*x[1]
                           for x in self.toppings['item_index']]
        dips_prices = [EXTRA_DIP[x[0]]['price']*x[1]
                       for x in self.dips['item_index']]
        sides_prices = [SIDES_MENU[x[0]]['price']*x[1]
                        for x in self.sides['item_index']]
        drinks_prices = [DRINKS_MENU[x[0]]['price']*x[1]
                         for x in self.drinks['item_index']]

        items_total = self.quantity * (self.pizza_price +
                                       sum(toppings_prices) +
                                       sum(dips_prices) +
                                       sum(sides_prices) +
                                       sum(drinks_prices)
                                       )
        return round(items_total, 2)

    def extras_summary(self, label_type='short'):
        """
        Combines labels and quantities of the selected extras.

        Args:
            label_type (str): Whether to return
                        shorthand ('short') or full labels.

        Returns:
            str: Concatenated summary string of extras.
        """
        extras_str_list = []
        for extra_full, extra_short in EXTRAS_NAMES:
            extra_counts = getattr(self, extra_full).get('counts')
            if extra_counts > 0:
                if label_type == 'full':
                    extras_str_list.append(f"{extra_full}:{extra_counts}")
                else:
                    extras_str_list.append(f"*{extra_short}:{extra_counts}")

        extras_str = f" - {' '.join(extras_str_list)}" if len(
            extras_str_list) > 0 else ''

        return extras_str


class Order():
    """
    Represents a full order containing 1 or more meals and other order details.

    Attributes:
        order_list (list): List of Meal objects in the order.
        total_price (float): Total cost of the full order.
        order_date (str): Timestamp when the order was created.
        last_orderID (int): The last numeric order ID for today's date.
        order_ID (str): Generated unique order ID based on date and
                        4-number digit in the format - yyyymmdd####.
    """

    def __init__(self, order_list, total_price, last_orderID):
        """
        Creates an instance order with a list of
            meals, total cost, and other order details.
        """
        self.order_list = order_list
        self.total_price = total_price
        datetime_now = datetime.now().astimezone(UK_TZONE)
        self.order_date = datetime_now.strftime(DATE_FORMAT)
        self.last_orderID = last_orderID
        self.order_ID = self.create_order_ID()

    @property
    def order_ready_time(self):
        """
        Calculates the order's ready time based on
            meal items quantity and extras included in each meal.

        Returns:
            str: datetime string for when the order should be ready.
        """
        BASE_MEAL_PREP_TIME = 10
        DELAY_pizza_PREP_TIME = 5

        pizza_count = sum([x.quantity for x in self.order_list])
        topping_sides = sum([x.toppings['counts']+x.sides['counts']
                            for x in self.order_list])
        preparation_time = BASE_MEAL_PREP_TIME

        if pizza_count > 2:
            preparation_time += ((pizza_count // 5) *
                                 DELAY_pizza_PREP_TIME)+DELAY_pizza_PREP_TIME

        if topping_sides > 0:
            preparation_time += ((topping_sides // 5) *
                                 DELAY_pizza_PREP_TIME)+DELAY_pizza_PREP_TIME

        ready_by_time = datetime.strptime(
            self.order_date, DATE_FORMAT) + \
            timedelta(minutes=preparation_time)

        return ready_by_time.replace(second=0).strftime(DATE_FORMAT)

    @property
    def order_items(self):
        """
        Combines order details into a summary for all items in the order.

        Returns:
            str: Concatenated item descriptions for all items in the order.
        """
        full_order_str = []
        for order_item in self.order_list:

            size_str = order_item.pizza_size.split(' - ')[0]
            name_str = order_item.pizza_name

            full_order_str.append(
                f"{order_item.quantity} x {size_str} "
                f"{name_str}{order_item.extras_summary('full')}")

        return ', '.join(full_order_str)

    @property
    def summary(self):
        """
        Creates a dictionary with key order details.

        Returns:
            dict: with keys including ID, date,
                  items, status, and total cost of the order.
        """
        return {
            "Order ID": self.order_ID,
            "Order date": self.order_date,
            "Order items": self.order_items,
            "Order ready time": self.order_ready_time,
            "Order status": 'Preparing',
            "Order total": self.total_price,
        }

    def create_order_ID(self):
        """
        Creates a unique order ID using the
            current date and incremented 4-digit number.

        Returns:
            str: Formatted order ID in the format - yyyymmdd####.
        """
        new_order_ID = datetime.today().strftime(DATE_FORMAT_ORDER) + \
            '{:04}'.format(self.last_orderID+1)

        return new_order_ID
