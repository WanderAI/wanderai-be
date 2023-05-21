import jwt
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta

class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"])
    secret = 'SECRET'
    
    def get_password_hash(self, passsword):
        return self.pwd_context.hash(passsword)
    
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def encode_token(self,user_id):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=300),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )
        
    def decode_token(self, token):
        try:
            payload = jwt.decode(token,self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=402, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=402, detail='Invalid token')
        
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
        
    

class JWTBearer(HTTPBearer):
    authHandler = AuthHandler()
    def __init__(self, auto_error:  bool = True):
        super(JWTBearer,self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer,self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Scheme Invalid")
            decoded = self.authHandler.decode_token(credentials.credentials)
            if decoded is not None:
                return decoded
        raise HTTPException(status_code=403, detail='Invalid token')
     