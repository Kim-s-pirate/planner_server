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

router = APIRouter(tags=["achievement"], prefix="/achievement")

load_dotenv(".env")
secret = os.getenv("secret")

# 책 id 받아서 총 성취량 보여주는 코드.
@router.get("/book_achievement/{book_id}", summary="책 id 총 성취도 조회", description="해당 책의 id로 총 성취도를 조회한다.", responses={
    200: {"description": "성취도 조회 성공", "content": {"application/json": {"example": {"message": "achievement data"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    403: {"description": "인증 실패", "content": {"application/json": {"example": {"message": "You are not authorized to view this book"}}}},
    404: {"description": "책 없음", "content": {"application/json": {"example": {"message": "Book not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 오류", "content": {"application/json": {"example": {"message": "achievement get failed"}}}}
})
async def book_achievement(request: Request, book_id: str):
    with get_db() as db:
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

# 날짜 두개랑 책 id 받아서 해당 책의 해당 기간동안의 성과 보여주는 코드.
@router.get("/period_book_achievement/{book_id}", summary="책 id 기간별 성취도 조회", description="해당 책의 id로 기간별 성취도를 조회한다.", responses={
    200: {"description": "성취도 조회 성공", "content": {"application/json": {"example": {"message": "achievement data"}}}},
    400: {"description": "잘못된 기간", "content": {"application/json": {"example": {"message": "Invalid Date Input"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    403: {"description": "인증 실패", "content": {"application/json": {"example": {"message": "You are not authorized to view this book"}}}},
    404: {"description": "책 없음", "content": {"application/json": {"example": {"message": "Book not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 오류", "content": {"application/json": {"example": {"message": "achievement get failed"}}}}
})
async def period_books_achievement(request: Request, start_date: date, end_date: date, book_id: str):
    with get_db() as db:
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
        except InvalidDateError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid Date Input"})
        except BookNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "achievement get failed"})
        
# 날짜 두개 받아서 그 사이의 성과 보여주는 코드. 그 사이 여러 책이 들어갈 수 있음
@router.get("/period_achievement", summary="여러 책 기간별 성취도 조회", description="여러 책의 기간별 성취도를 조회한다.", responses={
    200: {"description": "성취도 조회 성공", "content": {"application/json": {"example": {"message": "achievement data"}}}},
    400: {"description": "잘못된 기간", "content": {"application/json": {"example": {"message": "Invalid Date Input"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 오류", "content": {"application/json": {"example": {"message": "achievement get failed"}}}}
})
async def period_achievement(request: Request, start_date: date, end_date: date):
    with get_db() as db:
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
        except InvalidDateError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid Date Input"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "achievement get failed"})

# 날짜 하나와 책 id 받아서 그 날짜 이전까지의 해당 책의 진도율 보여주는 코드.
@router.get("/book_last_achievement/{book_id}", summary="특정 책의 특정 날짜 이전까지의 성취도 반환", description="해당하는 id를 가진 책의 주어진 date 이전까지의 성취도를 반환한다.", responses={
    200: {"description": "성취도 조회 성공", "content": {"application/json": {"example": {"message": "achievement data"}}}},
    400: {"description": "잘못된 날짜", "content": {"application/json": {"example": {"message": "Invalid Date Input"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    403: {"description": "인증 실패", "content": {"application/json": {"example": {"message": "You are not authorized to view this book"}}}},
    404: {"description": "책 없음", "content": {"application/json": {"example": {"message": "Book not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 오류", "content": {"application/json": {"example": {"message": "achievement get failed"}}}}
})
async def book_last_achievement(request: Request, last_date: date, book_id: str):
    with get_db() as db:
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
        except InvalidDateError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid Date Input"})
        except BookNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "achievement get failed"})

# 날짜 하나 받아서 그 날짜 이전까지의 진도율 보여주는 코드.
@router.get("/last_achievement", summary="특정 날짜 이전까지의 성취율 반환", description="주어진 date 이전까지의 성취도를 반환한다.", responses={
    200: {"description": "성취도 조회 성공", "content": {"application/json": {"example": {"message": "achievement data"}}}},
    400: {"description": "잘못된 날짜", "content": {"application/json": {"example": {"message": "Invalid Date Input"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 오류", "content": {"application/json": {"example": {"message": "achievement get failed"}}}}
})
async def last_books_achievement(request: Request, last_date: date):
    with get_db() as db:
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
        except InvalidDateError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid Date Input"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "achievement get failed"})

@router.get("/all_achievement", summary="모든 성취도 반환", description="사용자의 모든 성취도를 반환한다.", responses={
    200: {"description": "성취도 조회 성공", "content": {"application/json": {"example": {"message": "achievement data"}}}},
    400: {"description": "잘못된 기간", "content": {"application/json": {"example": {"message": "Invalid Date Input"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 오류", "content": {"application/json": {"example": {"message": "achievement get failed"}}}}
})
async def all_achievement(request: Request, start_date: date, end_date: date):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            progress = achievement_service.get_all_progress(start_date, end_date, requester_id, db)
            return JSONResponse(status_code=200, content={"message": progress})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except InvalidDateError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid Date Input"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "achievement get failed"})