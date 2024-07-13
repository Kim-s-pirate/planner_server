from fastapi.responses import JSONResponse
from Database.database import db
from Database.models import user
from fastapi import APIRouter
from Service.subject_service import subject_service
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *
from Data.subject import *

router = APIRouter()

@router.post("/subject_register")
async def subject_register(request: Request, subject_data: subject_register):
    try:
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=400, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=400, content={"message": "Token verification failed"})
        token = decode_token(token)
        subject_data = subject_service.to_subject_db(subject_data, token["userid"])
        subject_service.create_subject(subject_data)
        return JSONResponse(status_code=201, content={"message": "Subject registered successfully"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=409, content={"message": "Subject registration failed"})
    finally:
        db.commit()