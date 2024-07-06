from fastapi import HTTPException, Request
from jose import JWTError, jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv
from Service.authorization_service import *
load_dotenv("../.env")
secret = os.getenv("secret")

def get_token(request: Request):
    try:
        token = request.headers['Authorization']
        return token
    except:
        return False
    
def verify_token(token):
    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded_token  # 토큰이 유효한 경우 디코드된 토큰을 반환합니다.
    except InvalidTokenError:
        print("Invalid token")
        return False
    except JWTError:
        print("JWT Error")
        return False