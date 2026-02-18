from pydantic import BaseModel, field_serializer
from uuid import UUID
from datetime import datetime
from .inventory_schema import GetDestination

class HotelCreate(BaseModel):
    name: str
    destination_id: str
    address: str
    price_per_night: float
    latitude: float
    longitude: float

class GetHotel(BaseModel):
    hotel_id: UUID
    name: str
    destination_id: UUID
    address: str
    price_per_night: float
    latitude: float
    longitude: float
    created_at: datetime
    destination: GetDestination | None = None

    @field_serializer('hotel_id', 'destination_id')
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    class Config:
        from_attributes = True