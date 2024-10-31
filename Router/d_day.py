from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy import text
from Data.calendar import *
from Data.d_day import d_day_register
from Database.database import get_db, rollback_to_savepoint
from Data.user import *
from fastapi import APIRouter
from starlette.status import *
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from fastapi import Query, Request
from dotenv import load_dotenv

from Service.d_day_service import *

router = APIRouter(tags=["d_day"], prefix="/d_day")

@router.post("/create", summary="디데이 생성", description="디데이를 생성한다.", responses={
    201: {"description": "성공", "content": {"application/json": {"example": {"message": "D-Day created successfully"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "Error message"}}}}
})
async def create_d_day(request: Request, d_day_data: d_day_register):
    try:
        db = get_db()
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        d_day_service.create_d_day(d_day_data, user_id, db)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "D-Day created successfully"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()

@router.post("/edit/{id}", summary="디데이 수정", description="해당 id를 가진 디데이를 수정한다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "D-Day deleted successfully"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "Error message"}}}}
})
async def edit_d_day(request: Request, id: str, star: bool = Query(None)):
    try:
        db = get_db()
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        if star is None:
            raise ParameterError
        d_day_service.set_d_day_star(id, star, db)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "D-Day deleted successfully"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()

@router.get("/list", summary="디데이 리스트 반환", description="사용자의 디데이 리스트를 반환한다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": [{"id": "1", "name": "Sample D-Day"}]}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "Error message"}}}}
})
async def get_d_day_list(request: Request):
    try:
        db = get_db()
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        d_day_list = d_day_service.find_d_day_by_user_id(user_id, db)
        d_day_list = [d_day_service.to_d_day_data(d_day).dict() for d_day in d_day_list]
        return JSONResponse(status_code=200, content={"message": d_day_list})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()

@router.delete("/delete/{id}", summary="디데이 삭제", description="해당하는 id를 가진 디데이를 삭제한다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "D-Day deleted successfully"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "Error message"}}}}
})
async def delete_d_day(request: Request, id: str):
    try:
        db = get_db()
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        d_day_service.delete_d_day_by_id(id, db)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "D-Day deleted successfully"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()

# @router.post("/d_day/{id}")
# async def modify_d_day(request: Request, id: str, d_day_data: d_day_register):
#     try:
#         db = get_db()
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         d_day_service.modify_d_day(id, d_day_data, user_id, db)
#         db.commit()
#         return JSONResponse(status_code=200, content={"message": "D-Day modified successfully"})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": str(e)})
#     finally:
#         db.close()