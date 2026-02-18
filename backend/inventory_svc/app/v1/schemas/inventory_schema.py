from pydantic import BaseModel, field_serializer
from typing import Generic, TypeVar
from uuid import UUID
from datetime import datetime

T = TypeVar('T')

class ResponseWrapper(BaseModel, Generic[T]):
    status: str
    data: T

class AllDestinations(BaseModel):
    destination_id: str
    name: str
    description: str
    location: str
    created_at: str

class DestinationCreate(BaseModel):
    name: str
    country: str
    region: str | None = None
    description: str | None = None
    image_url: str | None = None
    tags: dict[str, int | str] | None = None

class GetDestination(BaseModel):
    destination_id: UUID
    name: str
    country: str
    region: str | None = None
    description: str | None = None
    image_url: str | None = None
    tags: dict[str, int | str] | None = None
    created_at: datetime

    @field_serializer('destination_id')
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    class Config:
        from_attributes = True