from fastapi.responses import JSONResponse
from Database.database import db, get_db
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.achievement_service import *
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from Service.authorization_service import *
router = APIRouter()
    
@router.get("/")
async def main(request: Request):
    try:
        return JSONResponse(status_code=200, content={"message": "Nice to meet you!"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error"})
    
# @router.get("/")
# async def main(request: Request):
#     token = get_token(request)
#     if token == False:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     verify = verify_token(token)
#     if verify == False:
#         return JSONResponse(status_code=401, content={"message": "Token verification failed"})
#     data = verify
#     return JSONResponse(status_code=200, content={"data":verify, "message": "Nice to meet you!"})

