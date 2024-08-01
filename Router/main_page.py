from fastapi.responses import JSONResponse
from Database.database import db
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from Service.authorization_service import *
router = APIRouter()
    
@router.get("/")
async def main(request: Request):
    try:
        from Controller.main import redis
        pong = await redis.ping()
        if pong == "PONG":
            print("존나 잘 되는 중")
        else:
            print("존나 잘 안되는 중")
            print(pong)
        return JSONResponse(status_code=200, content={"message": {
            "userid": "userid_placeholder",  # userid를 적절히 설정해야 함
            "exp": (datetime.now(timezone.utc) + timedelta(hours=1000000)).isoformat()  # ISO 포맷으로 변환
        }})
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=400, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=400, content={"message": "Token verification failed"})
        data = verify
        
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

