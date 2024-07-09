from fastapi import HTTPException, Request
from jose import JWTError, jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv
from Service.authorization_service import *
from datetime import datetime, timezone, timedelta
from Service.user_service import *

load_dotenv("../.env")
secret = os.getenv("secret")

def generate_token(email: str):
    userid = user_service.find_user_by_email(email).userid
    print(userid)
    payload = {
        "userid": userid,
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
        if user_service.find_user_by_userid(decoded_token["userid"]).userid == None:
            print("User not found")
            return False
    except InvalidTokenError:
        print("Invalid token")
        return False
    except JWTError:
        print("JWT Error")
        return False