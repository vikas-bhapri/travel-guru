from pydantic import BaseModel

class AllDestinations(BaseModel):
    destination_id: str
    name: str
    description: str
    location: str
    created_at: str