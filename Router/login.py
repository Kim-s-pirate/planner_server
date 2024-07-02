from fastapi.responses import JSONResponse
from Database.database import db
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from starlette.status import *

router = APIRouter()
    
@router.post("/login")
async def login(user_data: user_login):
    try:
        found_user = user_service.find_user_by_email(user_data.email)
        if found_user == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        if user_data.password != found_user.password:
            return JSONResponse(status_code=401, content={"message": "User login failed"})
        return JSONResponse(status_code=200, content={"message": "User logged in successfully"})
    except:
        return JSONResponse(status_code=409, content={"message": "There wes some error while logging in the user"})
