from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from models import Address
from dotenv import load_dotenv
import os

load_dotenv()

SHOP_ADDRESS = (
    os.getenv("SHOP_ADDRESS_NUMBER"),
    os.getenv("SHOP_ADDRESS_STREET"),
    os.getenv("SHOP_ADDRESS_CITY")
)
BASE_FEE = float(os.getenv("BASE_DELIVERY_FEE"))
PER_KM_FEE = float(os.getenv("PER_KM_DELIVERY_FEE"))

def get_coordinates(no, street, city):
    geolocator = Nominatim(user_agent="food_ordering_app")
    address = f"{no} {street}, {city}"
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else None

def calculate_distance(address: Address) -> float:
    coords1 = get_coordinates(address.number, address.street, address.city)
    coords2 = get_coordinates(*SHOP_ADDRESS)
    
    if coords1 and coords2:
        return geodesic(coords1, coords2).km
    return None

def calculate_delivery_fee(address: Address) -> dict:
    distance = calculate_distance(address)
    if distance is None:
        return {"fee": BASE_FEE, "distance": 0}
    
    fee = BASE_FEE + (distance * PER_KM_FEE)
    return {
        "fee": round(fee, 2),
        "distance": round(distance, 2)
    }