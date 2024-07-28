from fastapi.responses import JSONResponse
from Database.database import db
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *

router = APIRouter()

@router.post("/register")
async def register(user_data: user_register):
    try:
        if user_service.find_user_by_email(user_data.email) != None:
            return JSONResponse(status_code=409, content={"message": "email"})
        if user_service.find_user_by_userid(user_data.userid) != None:
            return JSONResponse(status_code=409, content={"message": "userid"})
        user_data = user_service.to_user_db(user_data)
        user_service.create_user(user_data)
        print(f"User {user_data.userid} registered")
        return JSONResponse(status_code=201, content={"message": "User registered successfully"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"message": "User registration failed"})
    finally:
        db.commit()
    
@router.get("/duplicate_id")
async def duplicate_id(userid: str):
    try:
        if user_service.find_user_by_userid(userid) == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        return JSONResponse(status_code=409, content={"message": "User already exists"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the user"})
    
@router.get("/duplicate_email")
async def duplicate_email(email: str):
    try:
        found_user = user_service.find_user_by_email(email)
        if found_user == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        return JSONResponse(status_code=409, content={"message": "User already exists"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the user"})

@router.delete("/user_delete/{user_id}")
async def user_delete(request: Request, user_id: str):
    try:
        userid = AuthorizationService.verify_session(request)
        if userid != user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this user"})
        user_service.delete_user(userid)
        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the user"})

@router.post("/edit_user/{current_userid}")
async def edit_user(request: Request, user_data: user_edit, current_userid: str):
    try:
        userid = AuthorizationService.verify_session(request)
        if userid != current_userid:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
        found_user = user_service.find_user_by_userid(current_userid)
        if found_user == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        user_service.edit_user(user_data, current_userid)
        modified_token = AuthorizationService.modify_session(request, current_userid)

        return JSONResponse(status_code=200, content={"message": "User edited successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        raise e
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "There was some error while editing the user"})
    finally:
        db.commit()
