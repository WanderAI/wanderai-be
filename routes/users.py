from uuid import uuid4
from fastapi import APIRouter, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi import FastAPI, Body
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
        raise HTTPException(status_code=405, detail="Email harus memiliki minimal 4 karakter")
    
    if len(inputUser.password) <= 5:
        raise HTTPException(status_code=405, detail="Password harus memiliki minimal 6 karakter")

    # Validate email format
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, inputUser.email):
        raise HTTPException(status_code=405, detail="Format email tidak valid")


    unique_id = str(uuid4())

    now = datetime.now(pytz.timezone('Asia/Jakarta'))

    print("datetime: ")
    print(now)

    hashed_password = AuthHandler().get_password_hash(inputUser.password)

    newUser = {"uuid": unique_id, "name": inputUser.name, "email": inputUser.email, "password": hashed_password, "createdAt": now}

    query = text("INSERT INTO user (uid, name, email, password, createdAt) VALUES (:uuid, :name, :email, :password, :createdAt)")
    try:
        dbInstance.conn.execute(query, newUser)
        return {"message": "Akun Berhasil Didaftarkan!"}
    except exc.SQLAlchemyError as e:
        error_msg = str(e)
        raise HTTPException(status_code=406, detail=error_msg)


@user_router.post('/login')
def login(inputUser: UserLoginSchema):
    users = dbInstance.conn.execute(text("SELECT email, password, name FROM user WHERE email=:email"), {"email":inputUser.email})
    hashed_password = AuthHandler().get_password_hash(passsword=inputUser.password)
    for user in users:
        if not AuthHandler().verify_password(plain_password=inputUser.password, hashed_password=user[1]):
            raise HTTPException(status_code=401, detail='Username atau password salah!')
            return
        name = user[2]
        firstName = name.split()[0]
        token = AuthHandler().encode_token(user.name)
        return {'message': f'login berhasil! Selamat datang, {firstName}!',
                'token': token}
    raise HTTPException(status_code=401, detail='Email tidak terdaftar!')
