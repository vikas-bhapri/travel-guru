from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import hotel_schema as schemas
from ..schemas.inventory_schema import ResponseWrapper
from ..database.db import get_async_session
from ..controllers import hotel_controller as hotel_ctrl

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_hotel(hotel: schemas.HotelCreate, db: AsyncSession = Depends(get_async_session)):
    result = await hotel_ctrl.create_hotel(hotel, db)
    return {"status": "success", "data": result}

@router.get("/{hotel_id}", status_code=status.HTTP_200_OK, response_model=ResponseWrapper[schemas.GetHotel])
async def get_hotel(hotel_id: str, db: AsyncSession = Depends(get_async_session)):
    result = await hotel_ctrl.get_hotel(hotel_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return {"status": "success", "data": result}
