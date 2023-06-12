from fastapi import APIRouter, Depends, HTTPException, Request, status, File, UploadFile
from fastapi.responses import JSONResponse
from models.events import ReccomendRequest
from services.auth import AuthHandler, JWTBearer
from services.database_manager import dbInstance
from sqlalchemy import text
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
import requests

event_router = APIRouter(
    tags=["Events"]
)

from fastapi import HTTPException

# @event_router.post("/get-format")
# async def getFormat(file: UploadFile = File(...), Authorize: JWTBearer = Depends(JWTBearer())):
#     try:
#         # Read the file content
#         content = await file.read()

#         try:
#             # Open the file using PIL library
#             image = Image.open(io.BytesIO(content))

#             # Get the format (JPEG or PNG)
#             file_info = {
#                 "format": image.format,
#                 "file_size": len(content) / (1024 * 1024),
#                 "filename": file.filename
#             }

#             # Set the success message
#             message = "success"
#             return {
#                 "message": message,
#                 "data": file_info
#             }
#         except OSError:
#             # Raise ValueError if the file is not an image
#             raise ValueError("File is not an image")

#     except ValueError as e:
#         return JSONResponse(status_code=400, content={"message": str(e)})

#     except HTTPException as e:
#         return JSONResponse(status_code=e.status_code, content={"message": e.detail})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"message": str(e)})

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
async def getRecommendation(request_data: ReccomendRequest, Authorize: JWTBearer = Depends(JWTBearer())):
    try:
        # Convert the request data to a JSON serializable format
        json_data = request_data.dict()

        # Make a POST request to the API endpoint
        response = requests.post("https://reccom-production-nzyzq3cmra-et.a.run.app/recommend", json=json_data)

        # Check if the request was successful
        if response.status_code == 200:
            # Return the response content
            return response.json()
        else:
            error_message = response.json()
            return JSONResponse(status_code=response.status_code, content=error_message)

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})