from fastapi.responses import JSONResponse
from Database.database import db
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from starlette.status import *

router = APIRouter()

@router.post("/register")
async def register(user_data: user_register):
    try:
        if user_service.find_user_by_email(user_data.email) != None:
            return JSONResponse(status_code=302, content={"message": "email"})
        if user_service.find_user_by_userid(user_data.userid) != None:
            return JSONResponse(status_code=302, content={"message": "userid"})
        user_data = user_service.to_user_db(user_data)
        user_service.create_user(user_data)
        print(f"User {user_data.userid} registered")
        return JSONResponse(status_code=201, content={"message": "User registered successfully"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=409, content={"message": "User registration failed"})
    finally:
        db.commit()
    
@router.post("/duplicate_id")
async def duplicate_id(userid: userid):
    try:
        userid = userid.userid
        if user_service.find_user_by_userid(userid) == None:
            return JSONResponse(status_code=200, content={"message": "User not found"})
        return JSONResponse(status_code=302, content={"message": "User already exists"})
    except:
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the user"})
    
@router.post("/duplicate_email")
async def duplicate_email(email: email):
    try:
        email = email.email
        found_user = user_service.find_user_by_email(email)
        if found_user == None:
            return JSONResponse(status_code=200, content={"message": "User not found"})
        return JSONResponse(status_code=302, content={"message": "User already exists"})
    except:
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the user"})

#임시 테스트용 엔드포인트 rollback 테스트
@router.get("/test")
async def test_rollback():
    try:
        # 임시 사용자 생성
        temp_user = user(email="temp@example.com", password="temp123", userid="temp123", username="temp")
        db.add(temp_user)
        # 여기서 갑자기 롤백
        db.rollback()
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Temporary user rolled back successfully"})
    except:
        return JSONResponse(status_code=409, content={"message": "There was some error while rolling back the user"})
    