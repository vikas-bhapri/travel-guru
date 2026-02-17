from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import inventory_schema as schemas
from ..database.db import get_async_session

router = APIRouter(
    prefix="/destinations",
    tags=["Destinations"]
)

@router.get("/")
async def get_all_destinations(db=Depends(get_async_session)):
    pass