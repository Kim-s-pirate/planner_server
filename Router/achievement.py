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

# 책 id 받아서 총 성취량 보여주는 코드.
@router.get("/achievement/book_achievement/{book_id}")
async def book_achievement(request: Request, book_id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(book_id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        progress = achievement_service.get_progress_by_book_id(book_id, db)
        return JSONResponse(status_code=200, content={"message": progress})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
    except BookNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "achievement get failed"})
    finally:
        db.close()

# 날짜 두개랑 책 id 받아서 해당 책의 해당 기간동안의 성과 보여주는 코드.
@router.get("/achievement/period_book_achievement/{book_id}")
async def period_book_achievement(request: Request, start_date: date, end_date: date, book_id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(book_id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        progress = achievement_service.get_book_progress_by_period(start_date, end_date, book_id, db)
        return JSONResponse(status_code=200, content={"message": progress})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
    except BookNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "achievement get failed"})
    finally:
        db.close()

# 날짜 두개 받아서 그 사이의 성과 보여주는 코드. 그 사이 여러 책이 들어갈 수 있음
@router.get("/achievement/period_achievement")
async def period_achievement(request: Request, start_date: date, end_date: date):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        progress = achievement_service.get_progress_by_period(start_date, end_date, requester_id, db)
        return JSONResponse(status_code=200, content={"message": progress})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "achievement get failed"})
    finally:
        db.close()

# 날짜 하나와 책 id 받아서 그 날짜 이전까지의 해당 책의 진도율 보여주는 코드.
@router.get("/achievement/book_last_achievement/{book_id}")
async def book_last_achievement(request: Request, last_date: date, book_id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(book_id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        progress = achievement_service.get_book_progress_before_date(last_date, book_id, db)
        return JSONResponse(status_code=200, content={"message": progress})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "achievement get failed"})
    finally:
        db.close()

# 날짜 하나 받아서 그 날짜 이전까지의 진도율 보여주는 코드.
@router.get("/achievement/last_achievement")
async def last_achievement(request: Request, last_date: date):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        progress = achievement_service.get_progress_before_date(last_date, requester_id, db)
        return JSONResponse(status_code=200, content={"message": progress})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "achievement get failed"})
    finally:
        db.close()

@router.get("/achievement/all_achievement")
async def all_achievement(request: Request, start_date: date, end_date: date):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        progress = achievement_service.get_all_progress(start_date, requester_id, requester_id, db)
        return JSONResponse(status_code=200, content={"message": progress})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "achievement get failed"})
    finally:
        db.close()