from fastapi import HTTPException, Request
from jose import JWTError, jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv
from Service.authorization_service import *
from datetime import datetime, timezone, timedelta

load_dotenv("../.env")
secret = os.getenv("secret")

def generate_token(email: str):
    payload = {
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)  # 1시간 후 만료
        }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def get_token(request: Request):
    try:
        token = request.headers['Authorization']
        return token
    except:
        return False
    
def decode_token(token):
    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded_token
    except InvalidTokenError:
        return False
    except JWTError:
        return False
    
def verify_token(token):
    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
        if decoded_token["exp"] < datetime.now(timezone.utc).timestamp():
            print("Token expired")
            return False
        else:
            return True  # 토큰이 유효한 경우 디코드된 토큰을 반환합니다.
    except InvalidTokenError:
        print("Invalid token")
        return False
    except JWTError:
        print("JWT Error")
        return False