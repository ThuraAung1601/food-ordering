from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AddressBase(BaseModel):
    number: str
    street: str
    city: str

class CustomerBase(BaseModel):
    username: str
    password: str
    name: str
    phone: str
    address: AddressBase

class AdminBase(BaseModel):
    username: str
    password: str
    staff_id: str

class ItemBase(BaseModel):
    name: str
    price: float
    description: str
    photo_url: Optional[str] = None

class MainDishBase(ItemBase):
    cooking_time: int

class SideDishBase(ItemBase):
    is_vegetarian: bool

class DrinkBase(ItemBase):
    temperature: str  # "hot" or "cold"

class CartItemBase(BaseModel):
    item_name: str
    quantity: int = 1

class OrderBase(BaseModel):
    delivery_address: Optional[AddressBase] = None
    save_address: bool = False 
    use_default_address: bool = True  

class OrderResponse(BaseModel):
    order_id: str
    items: List[ItemBase]
    delivery_address: str
    total_price: float
    delivery_fee: float  
    distance: float     
    estimated_delivery: datetime
    status: str

class CustomerResponse(BaseModel):
    username: str
    name: str
    default_address: str
    phone_number: str
    saved_addresses: List[str]
    active_orders: int
    cart_items: int