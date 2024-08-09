from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import get_db
from Data.user import *
from Database.models import user
from fastapi import APIRouter, Response, Request
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from dotenv import load_dotenv

router = APIRouter()

@router.post("/login")
async def login(request: Request, user_data: user_login):
    db = get_db()
    try:
        session_id = AuthorizationService.get_session(request)
        if session_id:
            verify = AuthorizationService.check_session(request)
            if verify:
                return JSONResponse(status_code=226, content={"message": "Already logged in"})
        found_user = user_service.find_user_by_email(user_data.email, db)
        if user_data.password != found_user.password:
            return JSONResponse(status_code=423, content={"message": "User login failed"})
        session_id = AuthorizationService.generate_session(found_user.userid, found_user.id)
        response = JSONResponse(
            status_code=200,
            content={"message": "User logged in successfully"}
        )
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    except UserNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": e.message})
    except Exception:
        return JSONResponse(status_code=500, content={"message": "There was some error while logging in the user"})
    finally:
        db.close()


@router.get("/logout")
async def logout(request: Request):
    db = get_db()
    try:
        AuthorizationService.verify_session(request, db)
        AuthorizationService.delete_session(request)
        return JSONResponse(status_code=200, content={"message": "User logged out successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while logging out the user"})
    finally:
        db.close()