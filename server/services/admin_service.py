import hashlib
from typing import Union, List
from database import get_admin, get_menu, update_menu, root, transaction  # Add transaction import
from models import Menu, MainDish, SideDish, Drink, DrinkTemperature
from schemas import MainDishBase, SideDishBase, DrinkBase, CustomerResponse
from typing import Dict, List
from models import Menu, Item

def authenticate_admin(username, password):
    admin = get_admin(username)
    if not admin:
        return None
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    return admin if admin.hash_password == hash_password else None

def create_menu(name):
    menu = Menu(name)
    update_menu(name, menu)
    return menu

def add_menu_item(menu_name: str, item_type: str, item_data: Union[MainDishBase, SideDishBase, DrinkBase]):
    menu = get_menu(menu_name)
    if not menu:
        return False
    
    item = None
    if item_type == "main":
        item = MainDish(item_data.name, item_data.price, item_data.description, item_data.cooking_time)
    elif item_type == "side":
        item = SideDish(item_data.name, item_data.price, item_data.description, item_data.is_vegetarian)
    elif item_type == "drink":
        temp = DrinkTemperature.COLD if item_data.temperature.lower() == "cold" else DrinkTemperature.HOT
        item = Drink(item_data.name, item_data.price, item_data.description, temp)
    
    if item:
        item.photo_url = item_data.photo_url
        menu.add_item(item)
        update_menu(menu_name, menu)
        return True
    return False

def get_all_customers() -> List[CustomerResponse]:
    from database import root
    customers_info = []
    for customer in root.users.values():
        customers_info.append(CustomerResponse(
            username=customer.username,
            name=customer._name,
            default_address=str(customer.default_address),
            phone_number=customer.phone_number,
            saved_addresses=[str(addr) for addr in customer.saved_addresses],
            active_orders=len(customer.orders),
            cart_items=len(customer.cart)
        ))
    return customers_info

def delete_menu(menu_name: str) -> bool:
    if menu_name not in root.menus:
        return False
    del root.menus[menu_name]
    transaction.commit()
    return True

def update_menu_item(menu_name: str, item_name: str, item_data: Union[MainDishBase, SideDishBase, DrinkBase]) -> bool:
    menu = get_menu(menu_name)
    if not menu:
        return False
    
    # Find and remove old item
    old_item = None
    for i, existing_item in enumerate(menu.items):
        if existing_item.name == item_name:
            old_item = menu.items.pop(i)
            break
    
    if not old_item:
        return False
    
    # Create new item with updated data
    item = None
    if isinstance(old_item, MainDish):
        item = MainDish(item_data.name, item_data.price, item_data.description, item_data.cooking_time)
    elif isinstance(old_item, SideDish):
        item = SideDish(item_data.name, item_data.price, item_data.description, item_data.is_vegetarian)
    elif isinstance(old_item, Drink):
        temp = DrinkTemperature.COLD if item_data.temperature.lower() == "cold" else DrinkTemperature.HOT
        item = Drink(item_data.name, item_data.price, item_data.description, temp)
    
    if item:
        item.photo_url = item_data.photo_url
        menu.add_item(item)
        update_menu(menu_name, menu)
        return True
    return False

def remove_menu_item(menu_name: str, item_name: str) -> bool:
    menu = get_menu(menu_name)
    if not menu:
        return False
    
    for item in menu.items:
        if item.name == item_name:
            menu.remove_item(item)
            update_menu(menu_name, menu)
            return True
    return False


def get_all_menus() -> Dict[str, Menu]:
    from database import root
    return dict(root.menus)

def get_menu_items(menu_name: str) -> List[Item]:
    menu = get_menu(menu_name)
    if not menu:
        return []
    return menu.items