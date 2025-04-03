from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services import admin_service,user_service
import os

router = APIRouter(tags=["auth"])

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))

@router.get("/login", response_class=HTMLResponse)
async def customer_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "static_path": "/static"
    })

@router.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data.get('username')
    password = data.get('password')
    
    # Try admin login first
    admin = admin_service.authenticate_admin(username, password)
    if admin:
        return {
            "message": "Login successful",
            "user_type": "admin",
            "redirect_path": "/admin/dashboard"
        }
    
    # If not admin, try customer login
    user = user_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "user_type": "customer",
        "redirect_path": f"/customers/{username}/dashboard"
    }