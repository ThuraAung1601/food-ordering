from database import get_user, add_user, get_item
from models import Customer, Address, Order
import hashlib
from schemas import AddressBase, OrderBase, OrderResponse, CartItemBase, ItemBase
from datetime import datetime, timedelta
from services.jwt_service import create_reset_token, verify_reset_token
from services.delivery_service import calculate_delivery_fee
from typing import Optional

def authenticate_user(username: str, password: str):
    user = get_user(username.lower())
    if not user or not isinstance(user, Customer):
        return None
    
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    return user if user.hash_password == hash_password else None

def create_user(username, password, name, number, street, city, phone):
    if get_user(username):
        return None
    
    address = Address(number, street, city)
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    user = Customer(username, password, hash_password, name, address, phone)
    return add_user(user)

def request_password_reset(username: str) -> Optional[str]:
    user = get_user(username)
    if not user:
        return None
    return create_reset_token(username)

def verify_reset_token_and_update_password(token: str, new_password: str) -> bool:
    username = verify_reset_token(token)
    if not username:
        return False
    
    user = get_user(username)
    if not user:
        return False
    
    hash_password = hashlib.sha256(new_password.encode()).hexdigest()
    user._password = new_password
    user._hash_password = hash_password
    return True

def reset_password(username: str, new_password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    
    hash_password = hashlib.sha256(new_password.encode()).hexdigest()
    user._password = new_password
    user._hash_password = hash_password
    return True

# Update create_order to include delivery fee
def create_order(username: str, address: Address = None) -> OrderResponse:
    user = get_user(username)
    if not user or not user.cart:
        return None
    
    delivery_info = calculate_delivery_fee(address or user.default_address)
    
    order = user.create_order(address or user.default_address)
    if not order:
        return None
    
    # Add delivery fee to total
    order.delivery_fee = delivery_info['fee']
    order.total_price += delivery_info['fee']
    order.distance = delivery_info['distance']
    
    return order

def add_delivery_address(username: str, address: Address):
    user = get_user(username)
    if not user:
        return False
    new_address = Address(address.number, address.street, address.city)
    user.add_delivery_address(new_address)
    return True

def confirm_order(username: str, delivery_address: str = None):
    user = get_user(username)
    if not user:
        return None
    order = user.confirm_order(delivery_address)
    if order:
        # Set estimated delivery time (e.g., 45 minutes)
        order.update_delivery_time(45)
    return order

def create_order(username: str, order_data: OrderBase) -> OrderResponse:
    user = get_user(username)
    if not user or not user.cart:
        return None

    # Determine delivery address
    delivery_address = None
    if order_data.use_default_address:
        delivery_address = user.default_address
    elif order_data.delivery_address:
        delivery_address = Address(
            order_data.delivery_address.number,
            order_data.delivery_address.street,
            order_data.delivery_address.city
        )
    
    if not delivery_address:
        return None

    # Calculate delivery fee
    delivery_info = calculate_delivery_fee(delivery_address)
    
    # Create order
    order = user.create_order(delivery_address)
    if not order:
        return None
    
    # Update order with delivery information
    order.delivery_fee = float(delivery_info['fee'])
    order.distance = float(delivery_info['distance'])
    order.total_price = sum(item.price for item in order.items) + order.delivery_fee
    
    # Create response
    return OrderResponse(
        order_id=str(order.created_at),
        items=[ItemBase(name=item.name, price=item.price, description=item.description) 
               for item in order.items],
        delivery_address=str(order.delivery_address),
        total_price=order.total_price,
        delivery_fee=order.delivery_fee,
        distance=order.distance,
        estimated_delivery=order.estimated_delivery_time or (datetime.now() + timedelta(minutes=45)),
        status=order.status.value
    )

def add_to_cart(username: str, cart_item: CartItemBase) -> bool:
    user = get_user(username)
    if not user:
        return False
    
    item = get_item(cart_item.item_name)
    if not item:
        return False
    
    for _ in range(cart_item.quantity):
        user.add_to_cart(item)
    return True