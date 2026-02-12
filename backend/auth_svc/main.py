from fastapi import FastAPI
from .database.database import engine
from .models import auth_model
from .routes import auth_routes


app = FastAPI(
    title="Travel Guru Auth Service",
    description="Authentication service for Travel Guru application.",
    version="0.1.0",
    contact={"name": "Vikas Bhapri", "email": "vikasbhapri@gmail.com"},
)

app.include_router(auth_routes.router)


@app.get("/")
async def hello_world():
    return {"message": "Welcome to the Travel Guru Auth Service!"}


auth_model.Base.metadata.create_all(bind=engine)
