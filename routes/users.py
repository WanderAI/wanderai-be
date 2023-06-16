from uuid import uuid4
from fastapi import APIRouter, Depends, Request, status, Query
from fastapi.responses import JSONResponse
from models.users import UserRegisterModel, UserLoginSchema, users, resetPasswordSchema, TokenStatus
from services.auth import AuthHandler, JWTBearer
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
        token = AuthHandler().encode_token(unique_id)
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
        token = AuthHandler().encode_token(user[3])
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

@user_router.post('/reset-password')
def resetPassword(inputUser: resetPasswordSchema, user_id: str = Depends(JWTBearer())):

    hashed_new_password = AuthHandler().get_password_hash(inputUser.newPassword)

    users = dbInstance.conn.execute(text("SELECT email, password, name, uid FROM user WHERE uid=:uid"), {"uid": user_id})
    for user in users:
        if not AuthHandler().verify_password(plain_password=inputUser.oldPassword, hashed_password=user[1]):
            return JSONResponse(status_code=400, content={"message": 'Password salah!'})
        update_query = text("UPDATE user SET password=:password WHERE uid=:uid")
        dbInstance.conn.execute(update_query, {"password": hashed_new_password, "uid": user_id})
        return {
            "message": 'success',
        }
    return JSONResponse(status_code=400, content={"message": 'Email tidak terdaftar!'})

@user_router.post('', response_model=dict)
def token_checker(user_id: str = Depends(JWTBearer())):
    users = dbInstance.conn.execute(text("SELECT email, password, name, uid FROM user WHERE uid=:uid"), {"uid": user_id})
    for user in users:
        return {
            "data": {
                "user_id": user[3],
                "email": user[0],
                "name": user[2]
            },
            "message": 'Success',
        }