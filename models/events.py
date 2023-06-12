from typing import List
from pydantic import BaseModel

class Restaurant(BaseModel):
    nama_restoran: str
    jarak_dari_tempat_meter: int
    kategori_harga: int
    rating_restaurant: float


class Response(BaseModel):
    confidence_percent: float
    place: dict
    nearest_restaurants: List[Restaurant]
    important_unique_facts: List[str]
    sejarah: str


class Request(BaseModel):
    imageFile: bytes

class ReccomendRequest(BaseModel):
    query: str
    city: str
    n_days: int
    n_people: int
    cost: int

    class Config:
        schema_extra = {
            "example": {
                "query": "Tempat untuk menikmati suasana alam",
                "city": "Bandung",
                "n_days": 5,
                "n_people": 2,
                "cost": 3
            }
        }