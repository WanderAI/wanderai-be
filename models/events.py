from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import geopy.distance

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

# Contoh penggunaan
request_data = {
    "imageFile": b"<binary_file_data>"
}

response_data = {
    "confidence_percent": 0.85,
    "place": {
        "nama": "Bandung",
        "summary": "Kota di Jawa Barat, Indonesia",
        "rating_tourism": 4.2
    },
    "nearest_restaurants": [
        {
            "nama_restoran": "Restoran A",
            "jarak_dari_tempat_meter": 200,
            "kategori_harga": 2,
            "rating_restaurant": 4.5
        },
        {
            "nama_restoran": "Restoran B",
            "jarak_dari_tempat_meter": 350,
            "kategori_harga": 3,
            "rating_restaurant": 4.2
        }
    ],
    "important_unique_facts": [
        "Bandung adalah kota kreatif",
        "Terkenal dengan makanan kulinernya"
    ],
    "sejarah": "Bandung didirikan pada tahun 1488 oleh Raja Jayadewata"
}

request_model = Request(**request_data)
response_model = Response(**response_data)

print(request_model.imageFile)
print(response_model.confidence_percent)
print(response_model.place)
print(response_model.nearest_restaurants)
print(response_model.important_unique_facts)
print(response_model.sejarah)