from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services import admin_service
from typing import Union
from schemas import MainDishBase, SideDishBase, DrinkBase, AdminBase

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="../templates")

@router.post("/login")
async def login_admin(admin: AdminBase):
    result = admin_service.authenticate_admin(admin.username, admin.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "message": "Login successful",
        "user_type": "admin",
        "redirect_path": "/admin/dashboard"
    }

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@router.post("/menu/create")
async def create_menu(name: str):
    menu = admin_service.create_menu(name)
    return {"message": "Menu created successfully", "menu_name": menu.name}

@router.delete("/menu/{menu_name}")
async def delete_menu(menu_name: str):
    success = admin_service.delete_menu(menu_name)
    if not success:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"message": "Menu deleted successfully"}

@router.post("/menu/{menu_name}/items")
async def add_menu_item(menu_name: str, item_type: str, item: Union[MainDishBase, SideDishBase, DrinkBase]):
    success = admin_service.add_menu_item(menu_name, item_type, item)
    if not success:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"message": "Item added successfully"}

@router.put("/menu/{menu_name}/items/{item_name}")
async def update_menu_item(menu_name: str, item_name: str, item: Union[MainDishBase, SideDishBase, DrinkBase]):
    success = admin_service.update_menu_item(menu_name, item_name, item)
    if not success:
        raise HTTPException(status_code=404, detail="Menu or item not found")
    return {"message": "Item updated successfully"}

@router.delete("/menu/{menu_name}/items/{item_name}")
async def remove_menu_item(menu_name: str, item_name: str):
    success = admin_service.remove_menu_item(menu_name, item_name)
    if not success:
        raise HTTPException(status_code=404, detail="Menu or item not found")
    return {"message": "Item removed successfully"}

@router.get("/customers")
async def get_all_customers():
    customers = admin_service.get_all_customers()
    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")
    return {"customers": customers}

@router.get("/menus")
async def get_all_menus():
    menus = admin_service.get_all_menus()
    return {
        "menus": [
            {
                "name": menu.name,
                "total_items": len(menu.items),
                "total_price": menu.total_price
            } for menu in menus.values()
        ]
    }

@router.get("/menu/{menu_name}/items")
async def get_menu_items(menu_name: str):
    items = admin_service.get_menu_items(menu_name)
    if not items:
        raise HTTPException(status_code=404, detail="Menu not found or empty")
    return {
        "menu_name": menu_name,
        "items": [
            {
                "name": item.name,
                "type": item.__class__.__name__,
                "price": item.price,
                "description": item.description,
                "photo_url": item.photo_url,
                **({"cooking_time": item.cooking_time} if hasattr(item, "cooking_time") else {}),
                **({"is_vegetarian": item.is_vegetarian} if hasattr(item, "is_vegetarian") else {}),
                **({"temperature": item.temperature.value} if hasattr(item, "temperature") else {})
            } for item in items
        ]
    }


@router.post("/logout")
async def logout_admin():
    return {"message": "Logged out successfully"}