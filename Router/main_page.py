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
    with get_db() as db:
        try:
            return JSONResponse(status_code=200, content={"message": "Nice to meet you!"})
        except Exception as e:
            return JSONResponse(status_code=409, content={"message": "There was some error"})

