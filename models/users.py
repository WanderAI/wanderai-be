from pydantic import BaseModel,EmailStr

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