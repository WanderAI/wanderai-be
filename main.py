from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from routes.events import event_router, getAverageBensin
from routes.users import user_router
from routes.shoetify import shoetify
import services.database_manager
from services.urlhandler import mapsapi
from models.events import Alamat

app = FastAPI()

app.include_router(event_router, prefix="/event")
app.include_router(user_router, prefix="/user")
app.mount("/shoetify", shoetify)

@app.get("/")
async def home():
    return {"message": "Welcome to Rey's API!"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000,
                log_level="info")

