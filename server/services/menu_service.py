from database import root
from typing import Dict, List

def get_all_menus() -> Dict:
    return {name: menu.items for name, menu in root.menus.items()}

def get_menu(menu_name: str) -> List:
    from database import root  # Import here to avoid circular import
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