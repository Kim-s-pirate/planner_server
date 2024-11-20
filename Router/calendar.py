from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy import text
from Data.calendar import *
from Database.database import get_db, rollback_to_savepoint
from Data.user import *
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from Service.calendar_service import *
from starlette.status import *
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from fastapi import Query, Request
from dotenv import load_dotenv

router = APIRouter(tags=["calendar"], prefix="/calendar")

@router.post("/create", summary="캘린더 생성", description="캘린더를 생성한다.", responses={
    201: {"description": "성공", "content": {"application/json": {"example": {"message": "Schedule registered successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "Schedule registration failed"}}}}
})
async def schedule_create(request: Request, schedule_data: day_schedule_register):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            if schedule_data.task_list is None:
                calendar_service.delete_schedule_by_date(schedule_data.date, requester_id, db)
            else:
                schedule_data = calendar_service.to_schedule_db(schedule_data, requester_id)
                calendar_service.create_schedule(schedule_data, db)
            return JSONResponse(status_code=201, content={"message": "Schedule registered successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Schedule registration failed"})

@router.get("/day_schedule/{date}", summary="하루 스케쥴 반환", description="주어진 date의 스케쥴을 반환한다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Schedule data"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    404: {"description": "스케줄 없음", "content": {"application/json": {"example": {"message": "Schedule not found"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "Schedule find failed"}}}}
})
async def get_day_schedule(request: Request, date: date):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            schedule = calendar_service.find_schedule_by_date(date, requester_id, db)
            if not schedule:
                raise ScheduleNotFoundError
            schedule = calendar_service.to_schedule_data(schedule)
            schedule = calendar_service.schedule_to_dict(schedule)
            del schedule['user_id']
            return JSONResponse(status_code=200, content={"message": schedule})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except ScheduleNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Schedule not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Schedule find failed"})

#month_schedule에는 일정과 월간, 주간 목표를 같이 보내줘야함
@router.get("/month_schedule", summary="달 스케쥴 반환", description="주어진 달의 스케쥴을 반환한다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Monthly schedule data"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    404: {"description": "스케줄 없음", "content": {"application/json": {"example": {"message": "Schedule not found"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "Schedule find failed"}}}}
})
async def get_month_schedule(request: Request, year: str, month: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            schedules = calendar_service.find_schedule_by_month(year, month, requester_id, db)
            if not schedules:
                raise ScheduleNotFoundError
            schedules = [calendar_service.to_schedule_data(schedule) for schedule in schedules]
            schedules = [calendar_service.schedule_to_dict(schedule) for schedule in schedules]
            for schedule in schedules:
                del schedule['user_id']
            return JSONResponse(status_code=200, content={"message": schedules})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except ScheduleNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Schedule not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Schedule find failed"})

@router.post("/register/goal", summary="목표 생성", description="캘린더의 목표를 생성한다.", responses={
    201: {"description": "성공", "content": {"application/json": {"example": {"message": "Goal registered successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "There was some error while registering the goal"}}}}
})
async def register_calendar_goal(request: Request, goal_data: calendar_goal_register):
    with get_db() as db:
        try:
            session = AuthorizationService.verify_session(request, db)
            user_id = session['id']
            if goal_data.goal is None:
                calendar_service.delete_goal(goal_data.year, goal_data.month, user_id, db)
            else:
                calendar_service.register_goal(goal_data, user_id, db)
            return JSONResponse(status_code=201, content={"message": "Goal registered successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "There was some error while registering the goal"})

@router.get("/calendar", summary="캘린더 반환", description="해당하는 달의 캘린더를 반환한다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"schedule": [{"id": "1", "name": "Sample Schedule"}], "goal": {"id": "1", "name": "Sample Goal"}}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "There was some error while getting the calendar"}}}}
})
async def get_calendar(request: Request, year: int, month: int):
    with get_db() as db:
        try:
            session = AuthorizationService.verify_session(request, db)
            user_id = session['id']
            schedule = calendar_service.find_schedule_by_month(year, month, user_id, db)
            goal = calendar_service.find_goal(year, month, user_id, db)
            data = {}
            if schedule:
                schedule = [calendar_service.to_schedule_data(s) for s in schedule]
                schedule = [calendar_service.schedule_to_dict(s) for s in schedule]
                for s in schedule:
                    del s['user_id']
                data['schedule'] = schedule
            if goal:
                goal = calendar_service.to_calendar_goal_data(goal).dict()
                del goal['user_id']
                data['goal'] = goal
            
            return JSONResponse(status_code=200, content=data)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "There was some error while getting the calendar"})



# @router.delete("/delete/day_schedule/{date}")
# async def delete_schedule(request: Request, date: date):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         requester_id = AuthorizationService.verify_session(request, db)["id"]
#         result = calendar_service.delete_schedule_by_date(date, requester_id, db)
#         if not result:
#             raise ScheduleNotFoundError
#         return JSONResponse(status_code=200, content={"message": "Schedule deleted successfully"})
#     except SessionIdNotFoundError as e:
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except ScheduleNotFoundError as e:
#         
#         return JSONResponse(status_code=404, content={"message": "Schedule not found"})
#     except Exception as e:
#         
#         return JSONResponse(status_code=500, content={"message": "Schedule delete failed"})
#     finally:
#         db.close()

# @router.delete("/delete/month_schedule")
# async def delete_schedule(request: Request, year: str, month: str):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         requester_id = AuthorizationService.verify_session(request, db)["id"]
#         result = calendar_service.delete_schedule_by_month(year, month, requester_id, db)
#         if not result:
#             raise ScheduleNotFoundError
#         return JSONResponse(status_code=200, content={"message": "Schedule deleted successfully"})
#     except SessionIdNotFoundError as e:
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except ScheduleNotFoundError as e:
#         
#         return JSONResponse(status_code=404, content={"message": "Schedule not found"})
#     except Exception as e:
#         
#         return JSONResponse(status_code=500, content={"message": "Schedule delete failed"})
#     finally:
#         db.close()

# #edit_calendar_goal 라우터 추가
# #값이 안들어왔을때 에러 처리
# @router.delete("/delete/goal")
# async def delete_calendar_goal(request: Request, year: int, month: int):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         calendar_service.delete_goal(year, month, user_id, db)
#         db.commit()
#         return JSONResponse(status_code=200, content={"message": "Goal deleted successfully"})
#     except SessionIdNotFoundError as e:
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except Exception as e:
#         
#         return JSONResponse(status_code=500, content={"message": "There was some error while deleting the goal"})
#     finally:
#         db.close()