import os
import secrets
from dotenv import load_dotenv
from fastapi import Request
from Service.authorization_service import *
from datetime import datetime, timezone, timedelta
from Service.user_service import *
from Service.error import *

# id

load_dotenv("../.env")
secret = os.getenv("secret")

class AuthorizationService:
    session_db:dict = {}

    # def session_id_list():
    #     return AuthorizationService.session_db.keys()

    def session_id_list(request: Request):
        session_ids = []
        for key in request.session.keys():
            if key == 'session_id':
                session_ids.append(request.session['session_id'])
        return session_ids

    def generate_session(request: Request, userid: str, id: str):
        session_id = secrets.token_hex(16)
        while session_id in AuthorizationService.session_id_list(request):
            session_id = secrets.token_hex(16)
        session_data = {
            'userid': userid,
            'id': id,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        request.session['session_id'] = session_id
        request.session['session_data'] = session_data
        return session_id
    
    def get_session(request: Request):
        print(AuthorizationService.session_id_list(request))
        session_id = request.session.get('session_id')
        if session_id is None:
            return False
        else:
            return session_id
        
    def check_session(request: Request):
        session_id = request.session.get('session_id')
        if session_id in AuthorizationService.session_id_list(request):
            return True
        return False
    
    @staticmethod
    def verify_session(request: Request, db):
        session_id = request.session.get('session_id')
        if session_id is None:
            raise SessionIdNotFoundError
        session = request.session.get('session_data')
        if session is None:
            raise SessionVerificationError
        if user_service.find_user_by_id(session['id'], db) is None:
            request.session.pop('session_id', None)
            request.session.pop('session_data', None)
            raise UserNotFoundError
        if datetime.fromisoformat(session['created_at']) + timedelta(hours=3) < datetime.now(timezone.utc):
            request.session.pop('session_id', None)
            request.session.pop('session_data', None)
            raise SessionExpiredError
        return session
    
    @staticmethod
    def delete_session(request: Request):
        session_id = request.session.get('session_id')
        if session_id is None:
            raise SessionIdNotFoundError
        request.session.pop('session_id', None)
        request.session.pop('session_data', None)
        return True
    
    @staticmethod
    def modify_session(request: Request, new_userid: str):
        session_id = request.session.get('session_id')
        if session_id is None:
            raise SessionIdNotFoundError
        session_data = request.session.get('session_data')
        if session_data is None:
            raise SessionVerificationError
        session_data['userid'] = new_userid
        request.session['session_data'] = session_data
        return True

    @staticmethod
    def check_authorization(id: str, another_id: str):
        if id != another_id:
            raise UnauthorizedError

