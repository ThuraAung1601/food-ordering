from fastapi import APIRouter, HTTPException
from services import menu_service
from typing import List

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("/")
async def get_all_menus():
    return menu_service.get_all_menus()

@router.get("/{menu_name}")
async def get_menu(menu_name: str):
    menu = menu_service.get_menu(menu_name)
    if not menu:
        raise HTTPException(status_code=404, message="Menu not found")
    return menu