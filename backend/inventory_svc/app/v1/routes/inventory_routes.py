from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import inventory_schema as schemas
from ..database.db import get_async_session
from ..controllers import destination_controller as dest_ctrl

router = APIRouter(
    prefix="/destinations",
    tags=["Destinations"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_destination(destination: schemas.DestinationCreate, db: AsyncSession = Depends(get_async_session)):
    result = await dest_ctrl.create_destination(destination, db)
    return {"status": "success", "data": result}

# @router.get("/", status_code=status.HTTP_200_OK)
# async def get_all_destinations(db: AsyncSession = Depends(get_async_session)):
#     result = await dest_ctrl.get_all_destinations(db)
#     return {"status": "success", "data": result}

@router.get("/{destination_id}", status_code=status.HTTP_200_OK)
async def get_destination(destination_id: str, db: AsyncSession = Depends(get_async_session)):
    result = await dest_ctrl.get_destination(destination_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return {"status": "success", "data": result}

@router.patch("/{destination_id}", status_code=status.HTTP_200_OK)
async def update_destination(destination_id: str, destination: schemas.DestinationCreate, db: AsyncSession = Depends(get_async_session)):
    result = await dest_ctrl.update_destination(destination_id, destination, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return {"status": "success", "data": result}

@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_destination(destination_id: str, db: AsyncSession = Depends(get_async_session)):
    result = await dest_ctrl.delete_destination(destination_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return {"status": "success", "message": "Destination deleted successfully"}

@router.get("/", status_code=status.HTTP_200_OK)
async def get_filtered_destinations(
    country: str | None = None,
    region: str | None = None,
    db: AsyncSession = Depends(get_async_session)
):
    filters = {}
    if country:
        filters["country"] = country
    if region:
        filters["region"] = region
    result = await dest_ctrl.get_filtered_destinations(filters, db)
    return {"status": "success", "data": result}
