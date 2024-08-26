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
        return JSONResponse(status_code=500, content={"message": "There was some error"})
    finally:
        db.close()

@router.get("/progresstest")
async def progresstest(request: Request, achiement_req: achievement_request, book_id: str):
    db = get_db()
    try:
        progress = achievement_service.get_book_progress_by_period(achiement_req, book_id, db)
        print(progress)
        return JSONResponse(status_code=200, content={"message": "Nice to meet you!"})
    except Exception as e:
        rollback_to_savepoint(db)
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error"})
    finally:
        db.close()

# @router.post("/get_result_by_date")
# async def get_result_by_date(request: Request, achievement_req: achievement_request):
#     db = get_db()
#     try:
#         requester_id = AuthorizationService.verify_session(request, db)["id"]
#         result = achievement_service.find_result_by_period(achievement_req, requester_id, db)
#         if not result:
#             return JSONResponse(status_code=404, content={"message": "No results found"})
#         return JSONResponse(status_code=200, content={"message": result})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         print(e)
#         return JSONResponse(status_code=409, content={"message": "There was some error"})
#     finally:
#         db.close()
#
#
# @router.post("/get_results_by_period")
# async def get_results_by_period(request: Request, achievement_req: achievement_request):
#     try:
#         db = get_db()
#         user_id = AuthorizationService.verify_session(request, db)["id"]
#         results = achievement_service.find_result_by_period(achievement_req, user_id, db)
#         if not results:
#             return JSONResponse(status_code=404, content={"message": "No results found for the period"})
#
#         # 중복된 book_id 제거
#         book_ids = list(set([res.book_id for res in results]))
#         progress_list = achievement_service.get_progress_by_book_id_list(book_ids, db)
#         return JSONResponse(status_code=200, content={"message": {"progress_list": progress_list}})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         print(e)
#         return JSONResponse(status_code=409, content={"message": "There was some error"})
#     finally:
#         db.close()
#
# @router.post("/get_progress_by_book_id")
# async def get_progress_by_book_id(request: Request, book_id: str):
#     try:
#         db = get_db()
#         progress = achievement_service.get_progress_by_book_id(book_id, db)
#         if progress is None:
#             return JSONResponse(status_code=404, content={"message": "No progress found for the given book ID"})
#         return JSONResponse(status_code=200, content={"progress": progress})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         print(e)
#         return JSONResponse(status_code=409, content={"message": "There was some error"})
#     finally:
#         db.close()
#
# @router.post("/get_progress_by_book_id_list")
# async def get_progress_by_book_id_list(request: Request, book_ids: List[str]):
#     try:
#         db = get_db()
#         progress_list = achievement_service.get_progress_by_book_id_list(book_ids, db)
#         return JSONResponse(status_code=200, content={"progress_list": progress_list})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         print(e)
#         return JSONResponse(status_code=409, content={"message": "There was some error"})
#     finally:
#         db.close()
#
# @router.post("/generate_dates_between")
# async def generate_dates_between(request: Request, achievement_req: achievement_request):
#     try:
#         dates = achievement_service.generate_dates_between(achievement_req.start_date, achievement_req.end_date)
#         return JSONResponse(status_code=200, content={"dates": dates})
#     except Exception as e:
#         print(e)
#         return JSONResponse(status_code=409, content={"message": "There was some error"})

