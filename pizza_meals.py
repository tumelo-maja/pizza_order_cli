from datetime import datetime, timedelta
from menu_items import (EXTRA_TOPPINGS, EXTRA_DIP, SIDES_MENU, DRINKS_MENU, EXTRAS_NAMES)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_ORDER = "%Y%m%d"
ORDER_NUMBER_LENGTH = 12

class Meal():
    """
    Creates a Meal instance
    """

    def __init__(self, pizza_name, pizza_base_toppings, pizza_size, pizza_price, toppings,dips,sides,drinks,quantity):
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
        
        description_str = f"{self.quantity} x {self.pizza_name} {self.pizza_size} {chr(0x1F355)} {self.extras_summary()}"
        price_str = self.total_price
        return description_str, price_str

    @property
    def total_price(self):
        
        toppings_prices = [EXTRA_TOPPINGS[x[0]]['price']*x[1] for x in self.toppings['item_indx']]
        dips_prices = [EXTRA_DIP[x[0]]['price']*x[1] for x in self.dips['item_indx']]
        sides_prices = [SIDES_MENU[x[0]]['price']*x[1] for x in self.sides['item_indx']]
        drinks_prices = [DRINKS_MENU[x[0]]['price']*x[1] for x in self.drinks['item_indx']]
        
        items_total = self.quantity * (self.pizza_price + 
                       sum(toppings_prices) + 
                       sum(dips_prices) +
                       sum(sides_prices) +
                       sum(drinks_prices)
                       )
        return round(items_total, 2)
    
    def extras_summary(self,label_type='short'):
        
        extras_str_list=[]
        for extra_full,extra_short in EXTRAS_NAMES:
            extra_counts =getattr(self, extra_full).get('counts')
            if extra_counts>0:
                if label_type == 'full':
                    extras_str_list.append(f"{extra_full}:{extra_counts}")
                else:
                    extras_str_list.append(f"*{extra_short}:{extra_counts}")


        extras_str = f" - {' '.join(extras_str_list)}" if len(extras_str_list) > 0 else ''
        
        return extras_str

class Order():
    """
    Creates an instance order.
    """

    def __init__(self, order_list, total_price,last_orderID):
        self.order_list = order_list
        self.total_price = total_price
        self.order_date = datetime.now().strftime(DATETIME_FORMAT)
        self.last_orderID = last_orderID
        self.order_ID = self.create_order_ID()

    @property
    def order_ready_time(self):
        BASE_MEAL_PREP_TIME = 15
        DELAY_pizza_PREP_TIME = 5
    
        pizza_count = sum([x.quantity for x in self.order_list])
        topping_sides = sum([x.toppings['counts']+x.sides['counts'] for x in self.order_list])
        preparation_time = BASE_MEAL_PREP_TIME
    
        if pizza_count > 2:
            preparation_time += ((pizza_count // 5) * DELAY_pizza_PREP_TIME)+DELAY_pizza_PREP_TIME
    
        if topping_sides > 0:
            preparation_time += ((topping_sides // 5) * DELAY_pizza_PREP_TIME)+DELAY_pizza_PREP_TIME
    
        ready_by_time = datetime.strptime(self.order_date, DATETIME_FORMAT) + timedelta(minutes=preparation_time)
            
        return ready_by_time.replace(second=0).strftime(DATETIME_FORMAT)

    @property
    def order_items(self):

        full_order_str = []
        for order_item in self.order_list:

            size_str = order_item.pizza_size.split(' - ')[0]
            name_str = order_item.pizza_name

            full_order_str.append(f"{order_item.quantity} x {size_str} {name_str}{order_item.extras_summary('full')}")

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
        new_order_ID = datetime.today().strftime(DATETIME_FORMAT_ORDER) + '{:04}'.format(self.last_orderID+1)
        
        return new_order_ID
