from database import root
from typing import Dict, List

def get_all_menus() -> Dict:
    return {name: menu.items for name, menu in root.menus.items()}

def get_menu(menu_name: str) -> List:
    from database import root  
    menu = root.menus.get(menu_name)
    return menu.items if menu else None

def find_item(item_name: str):
    for menu in root.menus.values():
        for item in menu.items:
            if item.name == item_name:
                return item
    return None

from typing import List, Optional
from models import Menu, Item

def get_menu_by_name(menu_name: str) -> Optional[Menu]:
    from database import root
    return root.menus.get(menu_name)

def get_menu_items_by_type(menu_name: str, item_type: str) -> List[Item]:
    menu = get_menu_by_name(menu_name)
    if not menu:
        return []
    return [item for item in menu.items if item.__class__.__name__.lower().startswith(item_type)]

def get_all_menus_with_items():
    menus_with_items = []
    for menu_name, menu in root.menus.items():
        menu_data = {
            "name": menu_name,
            "items": [
                {
                    "name": item.name,
                    "price": item.price,
                    "description": item.description,
                    "photo_url": item.photo_url,
                    "type": item.__class__.__name__,
                    **({"cooking_time": item.cooking_time} if hasattr(item, "cooking_time") else {}),
                    **({"is_vegetarian": item.is_vegetarian} if hasattr(item, "is_vegetarian") else {}),
                    **({"temperature": item.temperature.value} if hasattr(item, "temperature") else {})
                } for item in menu.items
            ]
        }
        menus_with_items.append(menu_data)
    return menus_with_items