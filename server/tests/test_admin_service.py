import unittest
from unittest.mock import Mock, patch
import sys
import os

os.environ['TESTING'] = 'true'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Admin, Menu, MainDish, SideDish, Drink, DrinkTemperature
from schemas import MainDishBase, SideDishBase, DrinkBase
from services.admin_service import *
from tests.mock_database import root  # Changed from relative import
import hashlib

class TestAdminService(unittest.TestCase):
    def setUp(self):
        root.menus.clear()
        root.admins.clear()
        
        # Setup admin with correct hash
        admin_password = "admin123"
        hash_password = hashlib.sha256(admin_password.encode()).hexdigest()
        self.admin = Admin("admin", admin_password, hash_password, "STAFF001")
        root.admins["admin"] = self.admin
        
        # Setup menu
        self.menu = Menu("Test Menu")
        root.menus["Test Menu"] = self.menu

    def test_authenticate_admin(self):
        """✅ Test admin authentication with valid and invalid credentials"""
        # Test valid credentials
        result = authenticate_admin("admin", "admin123")
        self.assertIsNotNone(result)
        
        # Test invalid password
        result = authenticate_admin("admin", "wrong_password")
        self.assertIsNone(result)
        
        # Test non-existent admin
        result = authenticate_admin("non_existent", "password")
        self.assertIsNone(result)

    def test_create_menu(self):
        """✅ Test menu creation and storage in database"""
        menu = create_menu("New Menu")
        self.assertEqual(menu.name, "New Menu")
        self.assertIn("New Menu", root.menus)

    def test_add_menu_item(self):
        """✅ Test adding different types of items to menu"""
        # Test adding main dish
        main_dish = MainDishBase(
            name="Test Burger",
            price=10.99,
            description="Test burger",
            cooking_time=15,
            photo_url="test.jpg"
        )
        success = add_menu_item("Test Menu", "main", main_dish)
        self.assertTrue(success)
        self.assertEqual(len(self.menu.items), 1)

        # Test adding to non-existent menu
        success = add_menu_item("Non-existent", "main", main_dish)
        self.assertFalse(success)

    def test_delete_menu(self):
        """✅ Test menu deletion with existing and non-existent menus"""
        success = delete_menu("Test Menu")
        self.assertTrue(success)
        self.assertNotIn("Test Menu", root.menus)

        success = delete_menu("Non-existent")
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()