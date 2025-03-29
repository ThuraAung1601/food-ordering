import unittest
from unittest.mock import Mock, patch
import sys
import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

os.environ['TESTING'] = 'true'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Customer, Address, MainDish, Order
from schemas import OrderBase, AddressBase, CartItemBase
from services.user_service import *
from services.jwt_service import create_reset_token, verify_reset_token
from tests.mock_database import root

class TestUserService(unittest.TestCase):
    def setUp(self):
        root.users.clear()
        
        # Setup test data
        self.test_password = "password123"
        self.hash_password = hashlib.sha256(self.test_password.encode()).hexdigest()
        self.test_address = Address("1", "Lat Krabang", "Bangkok")
        self.user = Customer(
            "testuser", 
            self.test_password, 
            self.hash_password,
            "Test User",
            self.test_address,
            "1234567890"
        )
        root.users["testuser"] = self.user
        
        # Setup test item
        self.test_item = MainDish("Test Burger", 10.99, "Test burger", 15)

    def test_password_reset_flow(self):
        """✅ Test the complete password reset flow with JWT"""
        # Test reset token request
        token = request_password_reset("testuser")
        self.assertIsNotNone(token)
        self.assertIsNone(request_password_reset("nonexistent"))

        # Test password reset with token
        new_password = "newpassword123"
        self.assertTrue(verify_reset_token_and_update_password(token, new_password))
        self.assertFalse(verify_reset_token_and_update_password("invalid_token", new_password))

        # Verify new password works
        result = authenticate_user("testuser", new_password)
        self.assertIsNotNone(result)

    # Remove test_authenticate_user_with_role method since we're not using roles

    def test_delivery_fee_calculation(self):
        """✅ Test delivery fee calculation"""
        # Add item to cart first
        self.user.add_to_cart(self.test_item)
        
        # Mock the delivery fee calculation
        with patch('services.delivery_service.calculate_delivery_fee') as mock_fee:
            mock_fee.return_value = {
                'fee': 9.52,
                'distance': 15.04
            }
            
            # Test order with default address
            order_data = OrderBase(
                delivery_address=None,
                save_address=False,
                use_default_address=True
            )
            order = create_order("testuser", order_data)
            self.assertIsNotNone(order)
            self.assertEqual(order.delivery_fee, 11.57)
            self.assertEqual(order.distance, 19.14)
            self.assertAlmostEqual(order.total_price, 22.56)  

    def test_authenticate_user(self):
        """✅ Test user authentication with valid and invalid credentials"""
        # Test valid credentials
        result = authenticate_user("testuser", self.test_password)
        self.assertIsNotNone(result)
        
        # Test invalid password
        result = authenticate_user("testuser", "wrong_password")
        self.assertIsNone(result)
        
        # Test non-existent user
        result = authenticate_user("non_existent", "password")
        self.assertIsNone(result)

    def test_create_user(self):
        """✅ Test user creation with new and duplicate usernames"""
        result = create_user("newuser", "password", "New User", 
                           "456", "New St", "New City", "0987654321")
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "newuser")
        
        # Test duplicate username
        result = create_user("testuser", "password", "Test User", 
                           "123", "Test St", "Test City", "1234567890")
        self.assertIsNone(result)

    def test_add_to_cart(self):
        """✅ Test adding items to cart and handling non-existent users"""
        # Test with CartItemBase
        cart_item = CartItemBase(item_name="Test Burger", quantity=1)
        
        # Mock both database functions
        with patch('services.user_service.get_user', return_value=self.user), \
             patch('services.user_service.get_item', return_value=self.test_item):
            
            success = add_to_cart("testuser", cart_item)
            self.assertTrue(success)
            self.assertEqual(len(self.user.cart), 1)
            
            # Clear cart for next test
            self.user.cart.clear()
            
            # Test non-existent user
            with patch('services.user_service.get_user', return_value=None):
                success = add_to_cart("non_existent", cart_item)
                self.assertFalse(success)

    def test_create_order(self):
        """✅ Test order creation with default and new delivery addresses"""
        # Add item to cart first
        self.user.add_to_cart(self.test_item)
        
        # Test order with default address
        order_data = OrderBase(
            delivery_address=None,
            save_address=False,
            use_default_address=True
        )
        order = create_order("testuser", order_data)
        self.assertIsNotNone(order)
        self.assertEqual(str(order.delivery_address), str(self.test_address))  # Use test_address instead of address
        
        # Add item to cart again for next test
        self.user.add_to_cart(self.test_item)
        
        # Test order with new address
        new_address = AddressBase(number="789", street="New St", city="New City")
        order_data = OrderBase(
            delivery_address=new_address,
            save_address=True,
            use_default_address=False
        )
        order = create_order("testuser", order_data)
        self.assertIsNotNone(order)
        self.assertIn(new_address.number, str(order.delivery_address))

if __name__ == '__main__':
    unittest.main()