from uuid import uuid4
from fastapi import APIRouter, Depends, Request, status
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from models.users import UserRegisterModel, UserLoginSchema, users
from services.auth import AuthHandler
from services.database_manager import dbInstance
from sqlalchemy import text, exc
import re
from datetime import datetime
import pytz

user_router = APIRouter(
    tags=["Users"]
)

@user_router.post('/register', status_code=201)
def register(inputUser: UserRegisterModel):
    if len(inputUser.email) <= 3:
        return JSONResponse(status_code=400, content={"message": "Email harus memiliki minimal 4 karakter"})
    
    if len(inputUser.password) <= 5:
        return JSONResponse(status_code=400, content={"message": "Password harus memiliki minimal 6 karakter"})

    # Validate email format
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, inputUser.email):
        return JSONResponse(status_code=400, content={"message": "Format email tidak valid"})

    unique_id = str(uuid4())

    now = datetime.now(pytz.timezone('Asia/Jakarta'))

    print("datetime: ")
    print(now)

    hashed_password = AuthHandler().get_password_hash(inputUser.password)

    newUser = {"uuid": unique_id, "name": inputUser.name, "email": inputUser.email, "password": hashed_password, "createdAt": now}

    query = text("INSERT INTO user (uid, name, email, password, createdAt) VALUES (:uuid, :name, :email, :password, :createdAt)")
    
    try:
        dbInstance.conn.execute(query, newUser)
        token = AuthHandler().encode_token(newUser["name"])
        return {
            "data": {
                "token": token,
                "uid": unique_id,
                "name": inputUser.name,
                "email": inputUser.email  # Add email to the response
            },
            "message": "Success",
        }
    except exc.IntegrityError as e:
        error_msg = str(e)
        if "Duplicate entry" in error_msg and "email" in error_msg:
            return JSONResponse(status_code=400, content={"message": "Email sudah terdaftar"})
        else:
            return JSONResponse(status_code=400, content={"message": error_msg})


@user_router.post('/login')
def login(inputUser: UserLoginSchema):
    # Validate email format
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, inputUser.email):
        return JSONResponse(status_code=400, content={"message": "Format email tidak valid"})

    users = dbInstance.conn.execute(text("SELECT email, password, name, uid FROM user WHERE email=:email"), {"email": inputUser.email})
    for user in users:
        if not AuthHandler().verify_password(plain_password=inputUser.password, hashed_password=user[1]):
            return JSONResponse(status_code=400, content={"message": 'Email atau password salah!'})
        name = user[2]
        firstName = name.split()[0]
        token = AuthHandler().encode_token(user[2])
        return {
            "data": {
                "token": token,
                "email": inputUser.email,
                "uid": user[3],
                "name": user[2]  # Add name to the response
            },
            "message": 'Success',
        }
    return JSONResponse(status_code=400, content={"message": 'Email tidak terdaftar!'})

