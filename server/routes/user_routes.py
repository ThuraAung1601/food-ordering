from fastapi import APIRouter, HTTPException,Request
from schemas import AddressBase, CustomerBase, CartItemBase, OrderBase
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from services import user_service,menu_service
from typing import List

router = APIRouter(prefix="/customers", tags=["customers"])
templates = Jinja2Templates(directory="../templates")

@router.post("/register")
async def register_user(customer: CustomerBase):
    user = user_service.create_user(
        customer.username, customer.password, customer.name,
        customer.address.number, customer.address.street, customer.address.city,
        customer.phone
    )
    if not user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully","username": customer.username}

@router.post("/{username}/address/add")
async def add_delivery_address(username: str, address: AddressBase):
    success = user_service.add_delivery_address(
        username,
        address  
    )
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Delivery address added successfully"}



@router.post("/login")
async def login_user(request: Request):
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        user = user_service.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return JSONResponse(content={
            "status": "success",
            "message": "Login successful",
            "user_type": "customer",
            "redirect_path": f"/customers/{username}/dashboard"
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#get all menus
@router.get("/{username}/menus", response_class=JSONResponse)
async def get_customer_menus(request: Request, username: str):
    menus = menu_service.get_all_menus_with_items()
    if not menus:
        raise HTTPException(status_code=404, detail="No menus found")
    menus_dict = {menu["name"]: menu["items"] for menu in menus}
    return JSONResponse(content={"username": username, "menus": menus_dict})


@router.get("/{username}/orders")
async def get_customer_orders(request: Request, username: str):
    orders = user_service.get_user_orders(username)
    return orders

@router.get("/{username}/dashboard", response_class=HTMLResponse)
async def customer_dashboard(request: Request, username: str):
    return templates.TemplateResponse("customer_dashboard.html", {
        "request": request,
        "username": username
    })


#get all items in the cart
@router.get("/{username}/cart")
async def get_cart_items(request: Request, username: str):
    cart_items = user_service.get_cart_items(username)

    if request.headers.get("accept") == "application/json":
        return cart_items
    else:
        return templates.TemplateResponse("customer_dashboard.html", {
            "request": request,
            "username": username,
            "cart_items": cart_items
        })
    
   
#add item to cart
@router.post("/{username}/cart/add")
async def add_to_cart(username: str, cart_item: CartItemBase):
    success = user_service.add_to_cart(username, cart_item)
    print(success)
    if not success:
        raise HTTPException(status_code=404, detail="User or item not found")
    return {"message": "Item added to cart"}


#remove item from cart
@router.delete("/{username}/cart/remove")
async def remove_from_cart(username: str, item_data: CartItemBase):
    success = user_service.remove_from_cart(username, item_data.item_name)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove item from cart")
    return {"message": "Item removed successfully"}

@router.post("/{username}/address/save")
async def save_delivery_address(username: str, address: AddressBase):
    success = user_service.add_saved_address(username, address)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Address saved successfully"}


@router.post("/{username}/order/create")
async def create_order(username: str):
    order_data = OrderBase(
        delivery_address=None,
        save_address=False,
        use_default_address=True
    )
    order = user_service.create_order(username, order_data)
    if not order:
        raise HTTPException(status_code=400, detail="Cart is empty")
    return {
        "message": "Order created successfully",
        "order_id": order.order_id,
        "delivery_address": order.delivery_address,
        "items": [{"name": item.name, "price": item.price} for item in order.items],
        "total_price": order.total_price,
        "delivery_fee": order.delivery_fee,
        "estimated_delivery": order.estimated_delivery
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


@router.get("/{username}/orders", response_class=HTMLResponse)
async def get_customer_orders(request: Request, username: str):
    orders = user_service.get_user_orders(username)
    menus = menu_service.get_all_menus_with_items()  
    return templates.TemplateResponse("customer_dashboard.html", {
        "request": request,
        "username": username,
        "orders": orders,
        "menus": menus  
    })


@router.post("/logout")
async def logout_customer():
    return {"message": "Logged out successfully"}