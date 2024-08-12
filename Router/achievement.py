from fastapi.responses import JSONResponse
from sqlalchemy import text
from Data.achievement import achievement_request
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter
from starlette.status import *
from Service.achievement_service import *
from Service.authorization_service import *
import os
from dotenv import load_dotenv
from fastapi import Request
from Data.book import *
from Service.book_service import *

router = APIRouter()

load_dotenv("../.env")
secret = os.getenv("secret")

@router.post("/test")
async def test(request: Request, achiement_req: achievement_request):
    try:
        db = get_db()
        result = achievement_service.generate_dates_between(achiement_req.start_date, achiement_req.end_date)
        print(result)
        return JSONResponse(status_code=200, content={"message": "Nice to meet you!"})
    except Exception as e:
        rollback_to_savepoint(db)
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error"})
    finally:
        db.close()