from fastapi import APIRouter, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi import FastAPI, Body
from models.users import UserRegisterModel, UserLoginSchema, users
from services.auth import AuthHandler
from services.database_manager import dbInstance
from sqlalchemy import text

user_router = APIRouter(
    tags=["Users"]
)

@user_router.post('/sign-up', status_code=201)
def register(inputUser: UserRegisterModel):
    if (len(inputUser.username) <= 3):
        raise HTTPException(status_code=405, detail="Username harus memiliki minilmal 4 karakter")
        return
    
    if (len(inputUser.password) <= 5):
        raise HTTPException(status_code=405, detail="Password harus memiliki minimal 6 karakter")
        return
    
    hashed_password = AuthHandler().get_password_hash(passsword=inputUser.password)

    newUser = {"fullName": inputUser.fullname, "username": inputUser.username, "password": hashed_password}

    query = text("INSERT INTO users (fullName, username, password) VALUES (:fullName, :username, :password)")
    try:
        dbInstance.conn.execute(query, newUser)
        return {"message": "Akun Berhasil Didaftarkan!"}
    except:
        raise HTTPException(status_code=406, detail="Username sudah diambil, silakah pilih username lain!")


@user_router.post('/sign-in')
def login(inputUser: UserLoginSchema):
    users = dbInstance.conn.execute(text("SELECT username, password, fullName FROM users WHERE username=:uname"), {"uname":inputUser.username})
    hashed_password = AuthHandler().get_password_hash(passsword=inputUser.password)
    for user in users:
        if not AuthHandler().verify_password(plain_password=inputUser.password, hashed_password=user[1]):
            raise HTTPException(status_code=401, detail='Username atau password salah!')
            return
        fullName = user[2]
        firstName = fullName.split()[0]
        token = AuthHandler().encode_token(user.username)
        return {'message': f'login berhasil! Selamat datang, {firstName}!',
                'token': token}
    raise HTTPException(status_code=401, detail='Username tidak terdaftar!')
