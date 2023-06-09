from pydantic import BaseModel
from datetime import datetime

class UserRegisterModel(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Rey Shazni",
                "email": "rey@gmail.com",
                "password": "weakpassword"
            }
        }

class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "rey@gmail.com",
                "password": "weakpassword"
            }
        }
        
users = []

class resetPasswordSchema(BaseModel):
    oldPassword: str
    newPassword: str

    class Config:
        schema_extra = {
            "example": {
                "oldPassword": "weakpassword",
                "newPassword": "newpassword"
            }
        }
        
users = []

class TokenStatus(BaseModel):
    token: str
    is_expired: bool
    expiration_date: datetime