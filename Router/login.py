from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import db, get_db
from Data.user import *
from Database.models import user
from fastapi import APIRouter, Response
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv("../.env")
secret = os.getenv("secret")
    
@router.post("/login")
async def login(user_data: user_login, request: Request, response: Response):
    try:
        db = get_db()
        session_id = AuthorizationService.get_session(request)
        if session_id:
            verify = AuthorizationService.check_session(request)
            if verify:
                return JSONResponse(status_code=226, content={"message": "Already logged in"})
            else:
                pass #토큰은 있는데 유효하지 않은 경우
        #이미 토큰이 있는 경우에 대해서 더 처리가 필요함.
        found_user = user_service.find_user_by_email(user_data.email, db)
        if found_user == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        if user_data.password != found_user.password:
            return JSONResponse(status_code=423, content={"message": "User login failed"})
        #여기에 들어가는 401코드는 변경되어야 함. 현재 토큰 처리에서 401을 사용하고 있기 때문에 401을 사용하면 토큰 처리로 인식됨.

        session_id = AuthorizationService.generate_session(found_user.userid)
        response = JSONResponse(
            status_code=200, 
            content={"message": "User logged in successfully"}
        )
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while logging in the user"})
    finally:
        db.close()

@router.get("/logout")
async def logout(request: Request, response: Response):
    try:
        db = get_db()
        session_id = AuthorizationService.verify_session(request, db)
        AuthorizationService.delete_session(request)
        return JSONResponse(status_code=200, content={"message": "User logged out successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "There was some error while logging out the user"})
    finally:
        db.close()