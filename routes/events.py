from fastapi import APIRouter, Depends, HTTPException, Request, status, File, UploadFile
from fastapi.responses import JSONResponse
from models.events import ReccomendRequest, RandomReccomendRequest
from services.auth import AuthHandler, JWTBearer
from random import choice, randint
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
import os
import pytz
from datetime import datetime, timedelta
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

def sanitize_objects_list(obj_list):
    sanitized_list = []
    for obj in obj_list:
        sanitized_obj = {}
        if "doc_id" in obj:
            sanitized_obj["doc_id"] = obj["doc_id"]
        if "city" in obj:
            sanitized_obj["city"] = obj["city"]
        if "created_date" in obj:
            sanitized_obj["created_date"] = obj["created_date"]
        if "date_start" in obj:
            sanitized_obj["date_start"] = obj["date_start"]
        if "date_end" in obj:
            sanitized_obj["date_end"] = obj["date_end"]
        sanitized_list.append(sanitized_obj)
    return sanitized_list

def generate_random_combination(date_start, date_end):
    # Define the valid options for each field
    valid_cities = ["Jakarta", "Bandung", "Yogyakarta", "Semarang", "Surabaya"]
    valid_costs = [1, 2, 3, 4]

    # Generate a random combination
    query = ""  # Sample query
    city = choice(valid_cities)

    n_people = randint(2, 6)  # Assuming maximum of 10 people
    cost = choice(valid_costs)

    # Return the random combination as a dictionary
    return {
        "query": query,
        "city": city,
        "day_start": date_start,
        "day_end": date_end,
        "n_people": n_people,
        "cost": cost
    }

@event_router.post("/recommendation-by-image")
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
            return {"message": "success", "data": response.json()}
        else:
            # Return an error message if the request failed
            error_message = response.json()
            {"message": error_message, "data": {}}

    except ValueError as e:
        return JSONResponse(status_code=401, content={"message": str(e), "data": {}})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e), "data": {}})

@event_router.post("/recommendation-random")
async def get_recommendation_random(inputUser: RandomReccomendRequest, user_id: str = Depends(JWTBearer())):
    try:
        request_data = generate_random_combination(inputUser.day_start, inputUser.day_end)

        # Convert the request data to a JSON serializable format
        json_data = {
            "query": request_data["query"],
            "city": request_data["city"],
            "day_start": request_data["day_start"],
            "day_end": request_data["day_end"],
            "n_people": request_data["n_people"],
            "cost": request_data["cost"]
        }

        # Calculate the number of days between day_start and day_end
        day_start = datetime.strptime(request_data["day_start"], "%d/%m/%Y").date()
        day_end = datetime.strptime(request_data["day_end"], "%d/%m/%Y").date()
        n_days = (day_end - day_start).days

        # Get the current date and time in Jakarta
        jakarta_timezone = pytz.timezone("Asia/Jakarta")
        current_datetime = datetime.now(jakarta_timezone)

        # Check if day_start is before the current date
        if day_start < current_datetime.date():
            return JSONResponse(status_code=400, content={"message": "Invalid day_start", "data": {}})

        # Remove day_start and day_end from request_data
        del request_data["day_start"]
        del request_data["day_end"]

        # Update the request data with n_days
        request_data["n_days"] = n_days + 1

        # Format the current date as "DD/MM/YYYY"
        formatted_date = current_datetime.strftime("%d/%m/%Y %H:%M:%S")

        # Make a POST request to the API endpoint
        response = requests.post("https://reccom-production-nzyzq3cmra-et.a.run.app/recommend", json=request_data)

        # Check if the request was successful
        if response.status_code == 200:
            # Store the response as a string in Firestore using the user's UID as the document ID
            doc_ref = db.collection('user_recommendation').document()
            doc_ref.set({
                "user_id": user_id,
                "city": json_data["city"],
                "date_start": json_data["day_start"],
                "date_end": json_data["day_end"],
                "data": response.text,
                "created_date": formatted_date,
            })

            # Return the response content
            return {
                "message": "success",
                "data": {
                    "doc_id": doc_ref.id,
                    "city": json_data["city"],
                    "date_start": json_data["day_start"],
                    "date_end": json_data["day_end"],
                }
            }
        else:
            error_message = response.json()
            return JSONResponse(status_code=response.status_code, content={"message": error_message, "data": {}})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message":str(e), "data": {}})


@event_router.post("/recommendation-by-payload")
async def get_recommendation(request_data: ReccomendRequest, user_id: str = Depends(JWTBearer())):
    try:
        # Convert the request data to a JSON serializable format
        json_data = request_data.dict()

        # Calculate the number of days between day_start and day_end
        day_start = datetime.strptime(request_data.day_start, "%d/%m/%Y").date()
        day_end = datetime.strptime(request_data.day_end, "%d/%m/%Y").date()
        n_days = (day_end - day_start).days

        # Get the current date and time in Jakarta
        jakarta_timezone = pytz.timezone("Asia/Jakarta")
        current_datetime = datetime.now(jakarta_timezone)

        # Check if day_start is before the current date
        if day_start < current_datetime.date():
            return JSONResponse(status_code=400, content={"message": "Invalid day_start", "data": {}})

        # Remove day_start and day_end from json_data
        del json_data["day_start"]
        del json_data["day_end"]

        # Update the request data with n_days
        json_data["n_days"] = n_days + 1

        # Format the current date as "DD/MM/YYYY"
        formatted_date = current_datetime.strftime("%d/%m/%Y %H:%M:%S")

        # Make a POST request to the API endpoint
        response = requests.post("https://reccom-production-nzyzq3cmra-et.a.run.app/recommend", json=json_data)

        # Check if the request was successful
        if response.status_code == 200:
            # Store the response as a string in Firestore using the user's UID as the document ID
            doc_ref = db.collection('user_recommendation').document()
            doc_ref.set({
                "user_id": user_id,
                "city": request_data.city,
                "date_start": request_data.day_start,
                "date_end": request_data.day_end,
                "data": response.text,
                "created_date": formatted_date,
            })

            # Return the response content
            return {
                "message": "success",
                "data": {
                    "doc_id": doc_ref.id,
                    "city": request_data.city,
                    "date_start": request_data.day_start,
                    "date_end": request_data.day_end,
                }
            }
        else:
            error_message = response.json()
            return JSONResponse(status_code=response.status_code, content={"message":str(e), "data": {}})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message":str(e), "data": {}})

@event_router.get("/list-recommendation-history")
async def getRecommendationHistory(user_id: str = Depends(JWTBearer())):
    try:
        query = db.collection('user_recommendation').where("user_id", "==", user_id).order_by("created_date", direction=firestore.Query.DESCENDING)
        results = query.get()

        recommendation_history = []
        for doc in results:
            recommendation_data = doc.to_dict()
            recommendation_data['doc_id'] = doc.id  # Add the document ID to the recommendation data
            # Extract the date part from created_date string in "DD/MM/YYYY" format
            recommendation_data['created_date'] = recommendation_data['created_date'].split()[0]
            sanitized_data = sanitize_data(recommendation_data)
            recommendation_history.append(sanitized_data)

        # Return the recommendation history
        final_data = sanitize_objects_list(recommendation_history)
        return {"message": "success", "data": final_data}

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e), "data": {}})

@event_router.get("/recommendation-detail/{doc_id}")
async def getRecommendationHistory(doc_id, Authorize: JWTBearer = Depends(JWTBearer())):
    try:
        # Get the Firestore document with the specified ID
        doc_ref = db.collection('user_recommendation').document(doc_id)
        results = doc_ref.get()

        recommendation_data = results.to_dict()
        sanitized_data = sanitize_data(recommendation_data)

        # Return the recommendation history
        return {"message": "success", "data": sanitized_data}

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e) , "data": {}})