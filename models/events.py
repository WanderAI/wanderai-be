from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

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
    day_start: str = Field(..., example="01/06/2023", description="Format: dd/mm/yyyy")
    day_end: str = Field(..., example="05/06/2023", description="Format: dd/mm/yyyy")
    n_people: int
    cost: int

    class Config:
        schema_extra = {
            "example": {
                "query": "Tempat untuk menikmati suasana alam",
                "city": "Bandung",
                "day_start": "01/08/2023",
                "day_end": "05/08/2023",
                "n_people": 2,
                "cost": 3
            }
        }

class RandomReccomendRequest(BaseModel):
    day_start: str = Field(..., example="01/06/2023", description="Format: dd/mm/yyyy")
    day_end: str = Field(..., example="05/06/2023", description="Format: dd/mm/yyyy")

    class Config:
        schema_extra = {
            "example": {
                "day_start": "01/08/2023",
                "day_end": "05/08/2023",
            }
        }