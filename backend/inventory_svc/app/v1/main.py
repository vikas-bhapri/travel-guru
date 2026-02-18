from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes import inventory_routes, hotel_routes
from .database.db import init_db, dispose_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables once
    await init_db()
    yield
    # Shutdown: Dispose of the engine
    await dispose_engine()

app = FastAPI(
    title="Travel Guru Inventory Service",
    description="Inventory management service for Travel Guru application.",
    version="0.1.0",
    contact={"name": "Vikas Bhapri", "email": "vikasbhapri@gmail.com"},
    root_path="/api/v1/inventory",
    lifespan=lifespan
)

app.include_router(inventory_routes.router)
app.include_router(hotel_routes.router)

@app.get("/")
async def hello_world():
    return {"message": "Welcome to the Travel Guru Inventory Service!"}