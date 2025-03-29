import unittest
from unittest.mock import patch
import os
from dotenv import load_dotenv
from services.delivery_service import calculate_delivery_fee, get_coordinates
from models import Address

load_dotenv()

class TestDeliveryService(unittest.TestCase):
    def setUp(self):
        self.test_address = Address(
            os.getenv("SHOP_ADDRESS_NUMBER"),
            os.getenv("SHOP_ADDRESS_STREET"),
            os.getenv("SHOP_ADDRESS_CITY")
        )
        self.mock_coords = (13.7563, 100.5018)  # Bangkok coordinates
        self.base_fee = float(os.getenv("BASE_DELIVERY_FEE"))
        self.per_km_fee = float(os.getenv("PER_KM_DELIVERY_FEE"))

    def test_get_coordinates(self):
        """✅ Test coordinate retrieval"""
        with patch('geopy.geocoders.Nominatim.geocode') as mock_geocode:
            mock_geocode.return_value.latitude = self.mock_coords[0]
            mock_geocode.return_value.longitude = self.mock_coords[1]
            
            coords = get_coordinates("123", "Test St", "Test City")
            self.assertEqual(coords, self.mock_coords)

    def test_delivery_fee_calculation(self):
        """✅ Test delivery fee calculation"""
        with patch('services.delivery_service.calculate_distance') as mock_distance:
            mock_distance.return_value = 5.0  # 5km distance
            
            result = calculate_delivery_fee(self.test_address)
            expected_fee = self.base_fee + (5.0 * self.per_km_fee)
            
            self.assertIsInstance(result, dict)
            self.assertIn('fee', result)
            self.assertIn('distance', result)
            self.assertEqual(result['distance'], 5.0)
            self.assertEqual(result['fee'], round(expected_fee, 2))

    def test_delivery_fee_invalid_address(self):
        """✅ Test delivery fee calculation with invalid address"""
        with patch('services.delivery_service.calculate_distance') as mock_distance:
            mock_distance.return_value = None
            
            result = calculate_delivery_fee(self.test_address)
            self.assertEqual(result['fee'], self.base_fee)
            self.assertEqual(result['distance'], 0)