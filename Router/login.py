from fastapi.responses import JSONResponse
from Database.database import db
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv("../.env")
secret = os.getenv("secret")
    
@router.post("/login")
async def login(user_data: user_login, request: Request):
    try:
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=401, content={"message": "Token verification failed"})
        #이미 토큰이 있는 경우에 대해서 더 처리가 필요함.
        found_user = user_service.find_user_by_email(user_data.email)
        if found_user == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        if user_data.password != found_user.password:
            return JSONResponse(status_code=401, content={"message": "User login failed"})
        #여기에 들어가는 401코드는 변경되어야 함. 현재 토큰 처리에서 401을 사용하고 있기 때문에 401을 사용하면 토큰 처리로 인식됨.
        payload = {
            "email": user_data.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)  # 1시간 후 만료
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return JSONResponse(status_code=200, content={"token": token, "message": "User logged in successfully"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error while logging in the user"})

