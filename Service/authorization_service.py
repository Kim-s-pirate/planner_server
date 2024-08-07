import os
import secrets
from dotenv import load_dotenv
from fastapi import Request
from Service.authorization_service import *
from datetime import datetime, timezone, timedelta
from Service.user_service import *

# id

# class TokenNotFoundError(Exception):
#     def __init__(self):
#         self.message = "Token not found"
#         super().__init__(self.message)

# class TokenVerificationError(Exception):
#     def __init__(self):
#         self.message = "Token verification failed"
#         super().__init__(self.message)

class SessionIdNotFoundError(Exception):
    def __init__(self):
        self.message = "Session ID not found"
        super().__init__(self.message)

class SessionVerificationError(Exception):
    def __init__(self):
        self.message = "Session verification failed"
        super().__init__(self.message)

class SessionExpiredError(Exception):
    def __init__(self):
        self.message = "Session expired"
        super().__init__(self.message)

load_dotenv("../.env")
secret = os.getenv("secret")



class AuthorizationService:
    session_db:dict = {}

    def session_id_list():
        return AuthorizationService.session_db.keys()

    def generate_session(userid: str, id: str):
        session_id = secrets.token_hex(16)
        while session_id in AuthorizationService.session_id_list():
            session_id = secrets.token_hex(16)
        AuthorizationService.session_db[session_id] = {
            'userid': userid,
            'id': id,
            'created_at': datetime.now(timezone.utc)
        }
        return session_id
    
    def get_session(request: Request):
        session_id = request.cookies.get('session_id')
        if session_id is None:
            return False
        else:
            return session_id
        
    def check_session(request: Request):
        session_id = request.cookies.get('session_id')
        if session_id in AuthorizationService.session_id_list():
            return True
    
    def verify_session(request: Request, db):
        session_id = request.cookies.get('session_id')
        if session_id is None:
            raise SessionIdNotFoundError
        if session_id not in AuthorizationService.session_id_list():
            raise SessionVerificationError
        session = AuthorizationService.session_db[session_id]
        if user_service.find_user_by_id(session['id'], db) is None:
            del AuthorizationService.session_db[session_id]
            raise UserNotFoundError
        if session['created_at'] + timedelta(hours=3) < datetime.now(timezone.utc):
            del AuthorizationService.session_db[session_id]
            raise SessionExpiredError
        return session
    #여기 부분도 userid를 주는게 아니라 원래 값을 반환하도록 해야함.
    
    def delete_session(request: Request):
        session_id = request.cookies.get('session_id')
        if session_id is None:
            raise SessionIdNotFoundError
        del AuthorizationService.session_db[session_id]
        return True
    
    def modify_session(request: Request, new_userid: str):
        session_id = request.cookies.get('session_id')
        if session_id is None:
            raise SessionIdNotFoundError
        AuthorizationService.session_db[session_id]['userid'] = new_userid
        return True
