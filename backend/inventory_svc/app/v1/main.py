from fastapi import FastAPI
from .routes import inventory_routes

app = FastAPI(
    title="Travel Guru Inventory Service",
    description="Inventory management service for Travel Guru application.",
    version="0.1.0",
    contact={"name": "Vikas Bhapri", "email": "vikasbhapri@gmail.com"},
    root_path="/api/v1/inventory"
)

app.include_router(inventory_routes.router)

@app.get("/")
async def hello_world():
    return {"message": "Welcome to the Travel Guru Inventory Service!"}