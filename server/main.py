from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from routes import user_routes, admin_routes, auth_routes
from database import initialize_database, close_connection
import os

app = FastAPI()

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Mount static files with correct path
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "static")), name="static")

# Configure templates with correct path
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database before starting the app
initialize_database()

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(admin_routes.router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("shutdown")
async def shutdown_event():
    close_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)