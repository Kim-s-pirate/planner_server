import json
from fastapi.responses import JSONResponse, RedirectResponse
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
from authlib.integrations.requests_client import OAuth2Session
from starlette.config import Config

router = APIRouter()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

oauth = OAuth2Session(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri=GOOGLE_REDIRECT_URI,
    scope='openid profile email',
    authorization_endpoint=GOOGLE_AUTHORIZATION_URL,
    token_endpoint=GOOGLE_TOKEN_URL,
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

# OAuth2
@router.get('/account/oauth2/login')
async def login(request: Request):
    # state = secrets.token_urlsafe(16)
    # request.session['state'] = state
    authorization_url, _ = oauth.create_authorization_url(GOOGLE_AUTHORIZATION_URL)
    return RedirectResponse(authorization_url)

@router.get('/account/login/oauth/google')
async def auth(request: Request):
    try:
        # Exchange authorization code for access token
        token = oauth.fetch_token(
            GOOGLE_TOKEN_URL,
            authorization_response=request.url._url,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )

        # Fetch user information
        user_info = oauth.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"})
        user_data = user_info.json()
        print(user_data)
        db = get_db()
        if user_service.find_user_by_email(user_data["email"], db):
            return JSONResponse(status_code=200, content={"message": "User logged in successfully"})
        else:
            return JSONResponse(status_code=404, content={"message": "User needs to register"})
        
        #여기서 프론트에서 작업을 해서 정보를 주면 추가해서 넣는 식으로 하면 될 것 같음.
        
    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": str(e)})

# 사용자 정보 API
@router.get('/account/user-info')
async def user_info(request: Request):
    try:
        token = request.cookies.get("access_token")
        if not token:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        
        user_info = await oauth.get(GOOGLE_USERINFO_URL, token=token)
        user_data = user_info.json()
        return JSONResponse(content={"user_info": user_data})
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": "Invalid token or error fetching user info"})