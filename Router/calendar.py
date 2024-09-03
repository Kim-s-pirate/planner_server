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
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from Service.authorization_service import *
import os
from fastapi import Query, Request
from dotenv import load_dotenv

router = APIRouter()

@router.post("/schedule/create")
async def schedule_create(request: Request, schedule_data: day_schedule_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        schedule_data = calendar_service.to_schedule_db(schedule_data, requester_id)
        calendar_service.create_schedule(schedule_data, db)
        return JSONResponse(status_code=201, content={"message": "Schedule registered successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "Schedule registration failed"})
    finally:
        db.close()

@router.get("/day_schedule/{date}")
async def get_day_schedule(request: Request, date: date):
    db = get_db()
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
    finally:
        db.close()

#month_schedule에는 일정과 월간, 주간 목표를 같이 보내줘야함
@router.get("/month_schedule")
async def get_month_schedule(request: Request, year: str, month: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        schedule = calendar_service.find_schedule_by_month(year, month, requester_id, db)
        if not schedule:
            raise ScheduleNotFoundError
        schedule = [calendar_service.to_schedule_data(s) for s in schedule]
        schedule = [calendar_service.schedule_to_dict(s) for s in schedule]
        for s in schedule:
            del s['user_id']
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
    finally:
        db.close()

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
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except ScheduleNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=404, content={"message": "Schedule not found"})
#     except Exception as e:
#         rollback_to_savepoint(db)
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
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except ScheduleNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=404, content={"message": "Schedule not found"})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": "Schedule delete failed"})
#     finally:
#         db.close()

#create에서 추가, 삭제, 생성을 모두 하는 식으로 변경
@router.post("/register/goal")
async def register_calendar_goal(request: Request, goal_data: calendar_goal_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        if goal_data.goal == None:
            calendar_service.delete_goal(goal_data.year, goal_data.month, user_id, db)
        else:
            calendar_service.register_goal(goal_data, user_id, db)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "Goal registered successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while registering the goal"})
    finally:
        db.close()

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
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": "There was some error while deleting the goal"})
#     finally:
#         db.close()

@router.get("/calendar")
async def get_calendar(request: Request, year: int, month: int):
    db = get_db()
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
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while getting the calendar"})

        