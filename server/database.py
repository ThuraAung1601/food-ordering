import ZODB, ZODB.FileStorage
import BTrees.OOBTree
import transaction
from models import Customer, Admin, Menu, Address, MainDish, SideDish, Drink, DrinkTemperature
import hashlib
import os

# Check if we're running tests
TESTING = os.environ.get('TESTING') == 'true'

if not TESTING:
    storage = ZODB.FileStorage.FileStorage('database.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()
else:
    from tests.mock_database import root

def initialize_database():
    global root
    print("Initializing database...")
    try:
        # Initialize users if not exists
        if not hasattr(root, 'users'):
            root.users = BTrees.OOBTree.BTree()
            # Add sample users
            address1 = Address("123", "Pyay", "Yangon")
            customer1 = Customer('customer1', 'password1', 'hash1', 'John Doe', address1, '555-0101')
            root.users[customer1.username] = customer1
            
        # Initialize other collections if needed
        if not hasattr(root, 'admins'):
            root.admins = BTrees.OOBTree.BTree()
            admin_password = "admin123"
            # Store only the hashed password
            hash_password = hashlib.sha256(admin_password.encode()).hexdigest()
            admin = Admin('admin', hash_password, hash_password, 'STAFF001')
            root.admins[admin.username] = admin

        # Initialize menus with sample items
        if not hasattr(root, 'menus'):
            root.menus = BTrees.OOBTree.BTree()
            
            # Create main menu with items
            main_menu = Menu("Main Menu")
            
            # Add main dishes
            burger = MainDish("Chicken Burger", 12.99, "Grilled chicken with fresh vegetables", 20)
            burger.photo_url = "/static/style/img/burger.png"
            burger.add_ingredient("Chicken patty")
            burger.add_ingredient("Lettuce")
            burger.add_ingredient("Tomato")
            
            pizza = MainDish("Pepperoni Pizza", 15.99, "Classic pepperoni pizza with mozzarella", 25)
            pizza.photo_url = "/static/style/img/pizza.png"
            pizza.add_ingredient("Pepperoni")
            pizza.add_ingredient("Mozzarella")
            
            # Add side dishes
            fries = SideDish("French Fries", 4.99, "Crispy golden fries", True)
            fries.photo_url = "/static/style/img/burger.png"
            
            salad = SideDish("Caesar Salad", 6.99, "Fresh romaine lettuce with caesar dressing", True)
            salad.photo_url = "/static/style/img/salad.png"
            
            # Add drinks
            cola = Drink("Coca Cola", 2.99, "Ice-cold cola", DrinkTemperature.COLD)
            cola.photo_url = "/static/style/img/pizza.png"
            
            coffee = Drink("Latte", 3.99, "Freshly brewed coffee with milk", DrinkTemperature.HOT)
            coffee.photo_url = "/static/style/img/burger.png"
            
            # Add all items to menu
            for item in [burger, pizza, fries, salad, cola, coffee]:
                main_menu.add_item(item)
            
            root.menus[main_menu.name] = main_menu

        # Initialize users if not exists
        if not hasattr(root, 'users'):
            root.users = BTrees.OOBTree.BTree()
        
        transaction.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        transaction.abort()

def get_admin(username: str) -> Admin:
    return root.admins.get(username.lower())

def get_menu(name: str) -> Menu:
    return root.menus.get(name)

def update_menu(name: str, menu: Menu) -> None:
    root.menus[name] = menu
    transaction.commit()

def delete_menu(name: str) -> bool:
    if name in root.menus:
        del root.menus[name]
        transaction.commit()
        return True
    return False

def get_item(item_name: str):
    for menu in root.menus.values():
        for item in menu.items:
            if item.name.lower() == item_name.lower():
                return item
    return None

def close_connection():
    connection.close()
    db.close()
    storage.close()


def get_user(username: str) -> Customer:
    return root.users.get(username.lower())

def add_user(user: Customer) -> Customer:
    if user.username.lower() in root.users:
        return None
    root.users[user.username.lower()] = user
    transaction.commit()
    return user