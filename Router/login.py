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
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
oauth = OAuth()

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:1500/auth',
    client_kwargs={'scope': 'openid profile email'},
)

@router.post("/account/login")
async def login(request: Request, user_data: user_login):
    db = get_db()
    try:
        session_id = AuthorizationService.get_session(request)
        if session_id:
            verify = AuthorizationService.check_session(request)
            if verify:
                raise DuplicateLoginError
        found_user = user_service.find_user_by_email(user_data.email, db)
        if not found_user or user_data.password != found_user.password:
            raise UserNotFoundError
        session_id = AuthorizationService.generate_session(found_user.userid, found_user.id)
        response = JSONResponse(
            status_code=200,
            content={"message": "User logged in successfully"}
        )
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    except DuplicateLoginError as e:
        return JSONResponse(status_code=226, content={"message": "Already logged in"})
    except UserNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": "ID or password does not match"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "User login failed"})
    finally:
        db.close()

@router.get("/account/logout")
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
    except SessionExpiredError as e:
        return JSONResponse(status_code=200, content={"message": "User logged out successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "There was some error while logging out the user"})
    finally:
        db.close()

#oauth2
@router.get('/account/oauth2/login')
async def login(request: Request):
    redirect_uri = os.getenv('REDIRECT_URI')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/account/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = await oauth.google.parse_id_token(request, token)
        # 여기서 얻은 사용자 정보를 이용해 필요한 작업을 수행
        return JSONResponse({
            "access_token": token["access_token"],
            "id_token": token["id_token"],
            "user_info": user
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})

# 사용자 정보 API
@router.get('/account/user-info')
async def user_info(token: str):
    try:
        user = await oauth.google.parse_id_token(Request, {"id_token": token})
        return JSONResponse({"user_info": user})
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": "Invalid token"})