from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import inventory_schema as schemas
from ..models import inventory_model as models

async def create_destination(destination: schemas.DestinationCreate, db: AsyncSession):
    new_destination = models.Destination(
        name = destination.name,
        country = destination.country,
        region = destination.region,
        description = destination.description,
        image_url = destination.image_url,
        tags = destination.tags
    )
    db.add(new_destination)
    await db.commit()
    await db.refresh(new_destination)
    return new_destination

async def get_destination(destination_id: str, db: AsyncSession):
    result = await db.get(models.Destination, destination_id)
    return result

async def get_all_destinations(db: AsyncSession):
    result = await db.execute(select(models.Destination))
    return result.scalars().all()

async def update_destination(destination_id: str, destination: schemas.DestinationCreate, db: AsyncSession):
    existing_destination = await db.get(models.Destination, destination_id)
    if not existing_destination:
        return None
    
    for field, value in destination.model_dump(exclude_unset=True).items():
        setattr(existing_destination, field, value)

    await db.commit()
    await db.refresh(existing_destination)
    return existing_destination

async def delete_destination(destination_id: str, db: AsyncSession):
    existing_destination = await db.get(models.Destination, destination_id)
    if not existing_destination:
        return None
    
    await db.delete(existing_destination)
    await db.commit()
    return True

async def get_filtered_destinations(filters: dict, db: AsyncSession):
    query = select(models.Destination)
    for field, value in filters.items():
        column = getattr(models.Destination, field)
        # Use case-insensitive comparison for string values
        if isinstance(value, str):
            query = query.where(column.ilike(f"%{value}%"))
        else:
            query = query.where(column == value)

    result = await db.execute(query)
    return result.scalars().all()
