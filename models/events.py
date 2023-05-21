from fastapi import FastAPI
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import geopy.distance

class Alamat(BaseModel):
    nama: str
    jalan: str
    kota: str

    class Config:
        schema_extra = {
            "example": {
                "nama": "rey shazni",
                "jalan": "Dago Asri 1 C-19",
                "kota": "Bandung"
            }
        }
    

class Bensin(BaseModel):
    pertamax: int
    pertalite: int
    solar: int

    class Config:
        schema_extra = {
            "example": {
                "pertamax": "10000",
                "pertalite": "8000",
                "solar": "6000"
            }
        }

class UpdateBensin(BaseModel):
    jenisBensin: str
    hargaBaru: int

    class Config:
        schema_extra = {
            "example": {
                "jenisBensin": "pertamax",
                "hargaBaru": "16000"
            }
        }