from fastapi import FastAPI

app = FastAPI(
    title="Travel Guru API",
    description="An API for managing travel-related data and services.",
    version="0.1.0",
    contact={"name": "Vikas Bhapri", "email": "vikasbhapri@gmail.com"},
)


@app.get("/")
async def hello_world():
    return {"message": "Welcome to the Travel Guru API!"}
