from fastapi import APIRouter, HTTPException
from schemas import AddressBase, CustomerBase
from services import user_service
from typing import List

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/register")
async def register_user(customer: CustomerBase):
    user = user_service.create_user(
        customer.username, customer.password, customer.name,
        customer.address.number, customer.address.street, customer.address.city,
        customer.phone
    )
    if not user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

@router.post("/{username}/address/add")
async def add_delivery_address(username: str, address: AddressBase):
    success = user_service.add_delivery_address(
        username,
        address  # Pass the entire address object
    )
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Delivery address added successfully"}

# Remove the duplicate address/add endpoint
@router.post("/login")
async def login_user(username: str, password: str):
    user = user_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

@router.post("/{username}/cart/add")
async def add_to_cart(username: str, item_name: str):
    success = user_service.add_to_cart(username, item_name)
    if not success:
        raise HTTPException(status_code=404, detail="User or item not found")
    return {"message": "Item added to cart"}

@router.post("/{username}/address/save")
async def save_delivery_address(username: str, address: AddressBase):
    success = user_service.add_saved_address(username, address)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Address saved successfully"}

@router.post("/{username}/order/create")
async def create_order(username: str, address: AddressBase = None):
    order = user_service.create_order(username, address)
    if not order:
        raise HTTPException(status_code=400, detail="Cart is empty")
    return {
        "message": "Order created successfully",
        "order_id": str(order.created_at),
        "delivery_address": str(order.delivery_address),
        "items": [{"name": item.name, "price": item.price} for item in order.items],
        "total_price": order.total_price,
        "estimated_delivery": order.estimated_delivery_time
    }

@router.post("/{username}/order/confirm")
async def confirm_order(username: str, address: AddressBase = None):
    order = user_service.confirm_order(username, address)
    if not order:
        raise HTTPException(status_code=400, detail="Cart is empty")
    return {
        "message": "Order confirmed",
        "order_id": str(order.created_at),
        "delivery_address": str(order.delivery_address),
        "estimated_delivery": order.estimated_delivery_time
    }

# Remove this duplicate route
# @router.post("/{username}/address/add")
# async def add_delivery_address(username: str, address: str):
#     success = user_service.add_delivery_address(username, address)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"message": "Delivery address added successfully"}

@router.post("/{username}/password-reset/request")
async def request_password_reset(username: str):
    token = user_service.request_password_reset(username)
    if not token:
        raise HTTPException(status_code=404, detail="User not found")
    return {"reset_token": token}

@router.post("/password-reset/complete")
async def reset_password(token: str, new_password: str):
    if not user_service.verify_reset_token_and_update_password(token, new_password):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password reset successful"}

@router.post("/{username}/password-reset/verify")
async def verify_reset_otp(username: str, otp: str):
    if not user_service.verify_reset_otp(username, otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"message": "OTP verified successfully"}

@router.post("/{username}/password-reset/complete")
async def reset_password(username: str, new_password: str):
    if not user_service.reset_password(username, new_password):
        raise HTTPException(status_code=400, detail="Password reset failed")
    return {"message": "Password reset successful"}