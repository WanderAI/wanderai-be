from fastapi import APIRouter, Depends, HTTPException, Request, status, File, UploadFile
from fastapi.responses import JSONResponse
from models.events import ReccomendRequest
from services.auth import AuthHandler, JWTBearer
from services.database_manager import dbInstance
from sqlalchemy import text
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
import os
import pytz
from datetime import datetime
import requests
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import json

credential_path = "serviceAccountKey.json"

cred = credentials.Certificate(credential_path)
firebase_admin.initialize_app(cred)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.
db = firestore.Client(project='wanderai-387006')

event_router = APIRouter(
    tags=["Events"]
)

from fastapi import HTTPException

def sanitize_data(json_object):
    if isinstance(json_object, dict):
        for key, value in json_object.items():
            if key == "data":
                try:
                    sanitized_data = json.loads(value)
                    json_object[key] = sanitized_data
                except json.JSONDecodeError:
                    # Handle invalid JSON data here if needed
                    pass
            else:
                sanitize_data(value)
    elif isinstance(json_object, list):
        for item in json_object:
            sanitize_data(item)

    return json_object

@event_router.post("/predict-image")
async def predictImage(file: UploadFile = File(...), Authorize: JWTBearer = Depends(JWTBearer())):
    try:
        # Read the file content
        content = await file.read()

        # Make sure the file is an image
        try:
            Image.open(io.BytesIO(content))
        except OSError:
            raise ValueError("Invalid file format")

        # Make a POST request to be-production.com
        response = requests.post("https://image-production-nzyzq3cmra-et.a.run.app/predict", files={"file": content})

        # Check if the request was successful
        if response.status_code == 200:
            # Return the response content
            return response.json()
        else:
            # Return an error message if the request failed
            error_message = response.json()
            return JSONResponse(status_code=response.status_code, content=error_message)

    except ValueError as e:
        return JSONResponse(status_code=401, content={"message": str(e), "detail": "File format should be image format."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

@event_router.post("/get-recommendation")
async def getRecommendation(request_data: ReccomendRequest, user_id: str = Depends(JWTBearer())):
    try:
        # Convert the request data to a JSON serializable format
        json_data = request_data.dict()

        # Get the current date and time in Jakarta
        jakarta_timezone = pytz.timezone("Asia/Jakarta")
        current_date = datetime.now(jakarta_timezone)

        # Format the current date as "DD/MM/YYYY"
        formatted_date = current_date.strftime("%d/%m/%Y")

        # Make a POST request to the API endpoint
        response = requests.post("https://reccom-production-nzyzq3cmra-et.a.run.app/recommend", json=json_data)

        # Check if the request was successful
        if response.status_code == 200:

            # Store the response as a string in Firestore using the user's UID as the document ID
            doc_ref = db.collection('user_recommendation').document()
            doc_ref.set({
                "user_id": user_id,
                "city": request_data.city,
                "data": response.text,
                "created_date": formatted_date
            })

            # Return the response content
            return response.json()
        else:
            error_message = response.json()
            return JSONResponse(status_code=response.status_code, content=error_message)

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

@event_router.post("/get-recommendation-history")
async def getRecommendationHistory(user_id: str = Depends(JWTBearer())):
    try:
        # Query the Firestore collection for user_recommendation with matching user_id
        query = db.collection('user_recommendation').where("user_id", "==", user_id)
        results = query.get()

        recommendation_history = []
        for doc in results:
            recommendation_data = doc.to_dict()
            sanitized_data = sanitize_data(recommendation_data)
            recommendation_history.append(sanitized_data)

        # Return the recommendation history
        return recommendation_history

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})