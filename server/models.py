import logging
import persistent
from abc import ABC, abstractmethod
from datetime import datetime, timedelta  
from enum import Enum
from typing import List  

class Account(ABC):
    def __init__(self, username, password, hash_password):
        self._username = username
        self._password = password
        self._hash_password = hash_password
        
    @property
    def username(self):
        return self._username
    
    @property
    def hash_password(self):
        return self._hash_password

class Admin(Account, persistent.Persistent):
    def __init__(self, username, password, hash_password, staff_id):
        super().__init__(username, password, hash_password)
        self.staff_id = staff_id
        self.menus = {}

    def manage_menu(self, menu, action='add'):
        if action == 'add':
            self.menus[menu.name] = menu
        elif action == 'remove' and menu.name in self.menus:
            del self.menus[menu.name]
        elif action == 'edit' and menu.name in self.menus:
            self.menus[menu.name] = menu

    @property
    def total_revenue(self):
        return sum(menu.total_price for menu in self.menus.values())

class Menu(persistent.Persistent):
    def __init__(self, name):
        self.name = name
        self._items = []

    @property
    def items(self):
        return self._items

    def add_item(self, item):
        if isinstance(item, Item):
            self._items.append(item)
            return True
        return False

    def remove_item(self, item):
        if item in self._items:
            self._items.remove(item)
            return True
        return False

    def edit_item(self, item):
        for i, existing_item in enumerate(self._items):
            if existing_item.name == item.name:
                self._items[i] = item
                return True
        return False

    @property
    def total_price(self):
        return sum(item.price for item in self._items)

class OrderStatus(Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Address(persistent.Persistent):
    def __init__(self, number, street, city):
        self.number = number
        self.street = street
        self.city = city

    def __str__(self):
        return f"{self.number} {self.street}, {self.city}"

    def __eq__(self, other):
        if not isinstance(other, Address):
            return False
        return (self.number == other.number and 
                self.street == other.street and 
                self.city == other.city)


class Customer(Account, persistent.Persistent):
    def __init__(self, username, password, hash_password, name, address, phone_number):
        super().__init__(username, password, hash_password)
        self._name = name
        self.default_address = address  
        self.phone_number = phone_number
        self.cart = []
        self.orders = []
        self.saved_addresses = [address]  

    def add_saved_address(self, address):
        if address not in self.saved_addresses:
            self.saved_addresses.append(address)
            return True
        return False

    def add_to_cart(self, item):
        self.cart.append(item)

    def clear_cart(self):
        self.cart = []

    def create_order(self, delivery_address=None):
        if not self.cart:
            return None
        address = delivery_address or self.default_address
        order = Order(self.cart.copy(), address)
        self.orders.append(order)
        self.clear_cart()
        return order

    def confirm_order(self, delivery_address=None):
        """Create and confirm a new order"""
        order = self.create_order(delivery_address)
        if order:
            order.confirm()
        return order

class Item(ABC, persistent.Persistent):
    def __init__(self, name, price, description, photo_url=None):
        self.name = name
        self.price = price
        self.description = description
        self.photo_url = photo_url
        self.ingredients = []

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

class MainDish(Item):
    def __init__(self, name, price, description, cooking_time):
        super().__init__(name, price, description)
        self.cooking_time = cooking_time

class SideDish(Item):
    def __init__(self, name, price, description, is_vegetarian):
        super().__init__(name, price, description)
        self.is_vegetarian = is_vegetarian

class DrinkTemperature(Enum):
    HOT = "hot"
    COLD = "cold"

class Drink(Item):
    def __init__(self, name, price, description, temperature):
        super().__init__(name, price, description)
        self.temperature = temperature

class Order(persistent.Persistent):
    def __init__(self, items: List[Item], delivery_address: Address):
        self.items = items
        self.delivery_address = delivery_address
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.estimated_delivery_time = None
        self._calculate_total()
        self._calculate_delivery_fee()
    
    def _calculate_delivery_fee(self):
        self.delivery_fee = 2.0 
    
    def _calculate_total(self):
        self.total_price = sum(item.price for item in self.items)
        if hasattr(self, 'delivery_fee'):
            self.total_price += self.delivery_fee
        self.distance = 0.0

    def update_delivery_time(self, minutes):
        self.estimated_delivery_time = datetime.now() + timedelta(minutes=minutes)

    def update_status(self, status):
        if isinstance(status, OrderStatus):
            self.status = status

    def confirm(self):
        """Confirm the order and set initial status"""
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.PREPARING
            if not self.estimated_delivery_time:
                self.update_delivery_time(45) 
            return True
        return False