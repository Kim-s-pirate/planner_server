from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy import text
from Data.calendar import *
from Data.d_day import d_day_register
from Database.database import get_db, rollback_to_savepoint
from Data.user import *
from fastapi import APIRouter
from starlette.status import *
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from fastapi import Query, Request
from dotenv import load_dotenv

from Service.d_day_service import *

router = APIRouter()

@router.post("/d_day/create")
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

@router.delete("/d_day/{id}")
async def delete_d_day(request: Request, id: str, star: bool = Query(None)):
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

@router.get("/d_day/list")
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

@router.delete("/d_day/{id}")
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