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
router = APIRouter(tags=["test"], prefix="/test")
    
@router.get("/", summary="테스트", description="테스트", response_description="테스트")
async def main(request: Request):
    try:
        db = get_db()

        achievement = achievement_service.get_progress_by_book_id("b280e3bb281dfd3807ddfc2f354d084d7725532a80f6fd08e3aaaeb3b2840ea3", db)
        print(achievement)
        get_progress_by_book_id_list = achievement_service.get_progress_by_book_id_list(["b280e3bb281dfd3807ddfc2f354d084d7725532a80f6fd08e3aaaeb3b2840ea3", "ceefb127424123b00c130c986a0ae03f6dbdc0703a9e769b8ef9d0a18ded5733"], db)
        print(get_progress_by_book_id_list)
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

