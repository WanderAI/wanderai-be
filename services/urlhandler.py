import requests
from dotenv import load_dotenv, dotenv_values
from models.events import Alamat
from fastapi import HTTPException


load_dotenv()
config = dotenv_values(".env")

api_key = config["API_KEY"]

class mapsapi():
    def getDrivingDistanceMaps(self, origin: Alamat, destination: Alamat):

        alamatOrigin = origin.jalan + origin.kota
        alamatDestination = destination.jalan + destination.kota

        if alamatDestination == alamatOrigin:
            raise HTTPException(status_code=406, detail="Alamat awal dan alamat tujuan tidak boleh sama!")


        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={alamatOrigin}&destinations={alamatDestination}&key={api_key}"

        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload).json()

        if response["rows"][0]["elements"][0]["status"] == "NOT_FOUND":
            raise HTTPException(status_code=406, detail="Masukkan alamat dengan benar!")

        return response

class daveroot():
    def getDaveRoot(self):

        headers = {
            'accept': 'application/json',
        }

        response = requests.get('http://128.199.149.182:8001/order_identity', headers=headers).json()
        return response


