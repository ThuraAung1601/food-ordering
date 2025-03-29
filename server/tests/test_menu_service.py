import unittest
from unittest.mock import Mock, patch
import sys
import os

os.environ['TESTING'] = 'true'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Menu, MainDish, SideDish, Drink, DrinkTemperature
from services.menu_service import *
from tests.mock_database import root  # Changed from relative import

class TestMenuService(unittest.TestCase):
    def setUp(self):
        # Clear mock database before each test
        root.menus.clear()
        
        # Setup test data
        self.mock_menu = Menu("Test Menu")
        self.mock_menu.add_item(MainDish("Burger", 10.99, "Test burger", 15))
        self.mock_menu.add_item(SideDish("Fries", 4.99, "Test fries", True))
        self.mock_menu.add_item(Drink("Cola", 2.99, "Test cola", DrinkTemperature.COLD))
        
        # Add menu to mock database
        root.menus["Test Menu"] = self.mock_menu

    def test_get_menu_by_name(self):
        """✅ Test retrieving menu by name with existing and non-existent menus"""
        # Test existing menu
        menu = get_menu_by_name("Test Menu")
        self.assertIsNotNone(menu)
        self.assertEqual(menu.name, "Test Menu")
        self.assertEqual(len(menu.items), 3)

        # Test non-existent menu
        menu = get_menu_by_name("Non-existent")
        self.assertIsNone(menu)

    def test_get_menu_items_by_type(self):
        """✅ Test filtering menu items by type (main, side, drink)"""
        # Test main dishes
        main_dishes = get_menu_items_by_type("Test Menu", "main")
        self.assertEqual(len(main_dishes), 1)
        self.assertIsInstance(main_dishes[0], MainDish)

        # Test side dishes
        side_dishes = get_menu_items_by_type("Test Menu", "side")
        self.assertEqual(len(side_dishes), 1)
        self.assertIsInstance(side_dishes[0], SideDish)

        # Test drinks
        drinks = get_menu_items_by_type("Test Menu", "drink")
        self.assertEqual(len(drinks), 1)
        self.assertIsInstance(drinks[0], Drink)

        # Test invalid menu
        items = get_menu_items_by_type("Non-existent", "main")
        self.assertEqual(len(items), 0)