from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import user_routes, admin_routes
from database import initialize_database, close_connection

app = FastAPI()

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
app.include_router(user_routes.router)
app.include_router(admin_routes.router)

@app.on_event("shutdown")
async def shutdown_event():
    close_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)