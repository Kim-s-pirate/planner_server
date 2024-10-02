import json
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from Data.oauth import *
from Database.database import get_db
from Data.user import *
from Database.models import user
from fastapi import APIRouter, Response, Request, requests
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
from starlette.config import Config
import urllib.parse
import requests

router = APIRouter()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")
NAVER_AUTHORIZATION_URI = os.getenv("NAVER_AUTHORIZATION_URI")
NAVER_TOKEN_URL = 'https://nid.naver.com/oauth2.0/token'
NAVER_USERINFO_URL = 'https://openapi.naver.com/v1/nid/me'

oauth_google = OAuth2Session(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri=GOOGLE_REDIRECT_URI,
    scope='openid profile email',
    authorization_endpoint=GOOGLE_AUTHORIZATION_URL,
    token_endpoint=GOOGLE_TOKEN_URL,
)

oauth_naver = OAuth2Session(NAVER_CLIENT_ID, redirect_uri=NAVER_AUTHORIZATION_URI)

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
        session_id = AuthorizationService.generate_session(request, found_user.userid, found_user.id)
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
        raise e
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

# OAuth2
@router.get('/account/oauth2/login')
async def login(request: Request):
    # state = secrets.token_urlsafe(16)
    # request.session['state'] = state
    authorization_url, _ = oauth_google.create_authorization_url(GOOGLE_AUTHORIZATION_URL)
    return RedirectResponse(authorization_url)

@router.get('/account/login/oauth/google')
async def auth(request: Request):
    try:
        # Exchange authorization code for access token
        token = oauth_google.fetch_token(
            GOOGLE_TOKEN_URL,
            authorization_response=request.url._url,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )

        # Fetch user information
        user_info = oauth_google.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"})
        user_data = user_info.json()
        print(user_data)
        db = get_db()
        if user_service.find_user_by_email(user_data["email"], db):
            return JSONResponse(status_code=200, content={"message": "User logged in successfully"})
        else:
            return JSONResponse(status_code=404, content={"message": "User needs to register"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    
@router.get("/account/oauth2/naver/get_state")
async def get_state(request: Request):
    try:
        state = secrets.token_urlsafe(16)
        request.session['state'] = state
        print("state: "+state)
        response = JSONResponse(status_code=200, content={"state": state})
        response.set_cookie(key="state", value=state, httponly=True, samesite="None", secure=True)
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

@router.post('/account/login/oauth/naver')
async def auth(request: Request, naver_data: naver_data):
    try:
        code = naver_data.code
        state = naver_data.state
        cookie_state = request.cookies.get("state")
        print(request.session.get("state"))
        print(request.cookies)
        print(state)
        print(cookie_state)
        if state != cookie_state:
            return JSONResponse(status_code=401, content={"message": "Invalid state"})
        token = oauth_naver.fetch_token(
            NAVER_TOKEN_URL,
            client_id=NAVER_CLIENT_ID,
            client_secret=NAVER_CLIENT_SECRET,
            code = code,
            state = state,
            grant_type="authorization_code"
        )
        response = requests.get(
            NAVER_USERINFO_URL,
            headers={"Authorization": f"Bearer {token['access_token']}"}
        )
        user_data = response.json()
        print(user_data)

        db = get_db()
        if user_service.find_user_by_email(user_data["response"]["email"], db):
            return JSONResponse(status_code=200, content={"message": "User logged in successfully"})
        else:
            return JSONResponse(status_code=404, content={"message": "User needs to register", "user_email": user_data["response"]["email"]})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    

@router.post("/account/sound_setting")
async def sound_setting(request: Request, sound_setting: int):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        if user_service.update_user_sound_setting(user_id, sound_setting, db):
            return JSONResponse(status_code=200, content={"message": "Sound setting updated successfully"})
        else:
            raise Exception
    except InvalidSoundSettingError as e:
        return JSONResponse(status_code=400, content={"message": "Invalid sound setting"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Sound setting update failed"})
    finally:
        db.close()