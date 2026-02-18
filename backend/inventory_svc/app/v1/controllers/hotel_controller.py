from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..schemas import hotel_schema as schemas
from ..models.inventory_model import Hotel, Destination

async def create_hotel(hotel: schemas.HotelCreate, db: AsyncSession):
    new_hotel = Hotel(
        name = hotel.name,
        destination_id = hotel.destination_id,
        address = hotel.address,
        price_per_night = hotel.price_per_night,
        latitude = hotel.latitude,
        longitude = hotel.longitude
    )
    db.add(new_hotel)
    await db.commit()
    await db.refresh(new_hotel)
    return new_hotel

async def get_hotel(hotel_id: str, db: AsyncSession):
    # Eager load the destination relationship to avoid lazy loading issues
    query = select(Hotel).where(Hotel.hotel_id == hotel_id).options(selectinload(Hotel.destination))
    result = await db.execute(query)
    return result.scalar_one_or_none()