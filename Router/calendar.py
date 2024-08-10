from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy import text
from Data.schedule import day_schedule, day_schedule_register
from Data.calendar import calendar_goal_register, calendar_goal
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

@router.post("/register_schedule")
async def register_schedule(schedule_data: day_schedule_register, request: Request):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))

        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']

        calendar_service.delete_schedule(schedule_data.date, user_id, db)

        schedule_data = calendar_service.to_schedule_db(schedule_data, user_id)

        calendar_service.register_schedule(schedule_data, db)

        db.commit()

        return JSONResponse(status_code=200, content={"message": "Schedule registered successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        raise e
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while registering the schedule"})

    finally:
        db.close()

@router.get("/get_day_schedule")
async def get_day_schedule(request: Request, date: date):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        schedule = calendar_service.find_schedule_by_date(date, user_id, db)
        schedule = calendar_service.to_schedule_data(schedule)
        schedule = calendar_service.schedule_to_dict(schedule)
        return JSONResponse(status_code=200, content={"message": schedule})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while getting the schedule"})

    finally:
        db.close()

# 이부분을 굳이 param으로 할 이유는 없을 듯
@router.get("/get_month_schedule")
async def get_month_schedule(request: Request, year: str = Query(None), month: str = Query(None)):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']

        schedule = calendar_service.get_month_schedule(year, month, user_id, db)

        schedule = [calendar_service.to_schedule_data(s) for s in schedule]

        schedule = [calendar_service.schedule_to_dict(s) for s in schedule]
        for s in schedule:
            del s['user_id']
        return JSONResponse(status_code=200, content={"message": schedule})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while getting the schedule"})

    finally:
        db.close()

# task_list를 찢어서 따로 만들어서 특정 task를 수정할 수 있도록 수정

@router.delete("/delete_schedule")
async def delete_schedule(request: Request, date: date = Query(None)):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        calendar_service.delete_schedule(date, user_id, db)

        db.commit()

        return JSONResponse(status_code=200, content={"message": "Schedule deleted successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the schedule"})

    finally:
        db.close()

# 월단위 delete 필요성 고민

@router.post("/register_calendar_goal")
async def register_calendar_goal(goal_data: calendar_goal_register, request: Request):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))

        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']

        if goal_data.month_goal == None and goal_data.week_goal == None:
            calendar_service.delete_goal(goal_data.year, goal_data.month, user_id, db)
        else:
            calendar_service.register_goal(goal_data, user_id, db)

        db.commit()

        return JSONResponse(status_code=200, content={"message": "Goal registered successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while registering the goal"})

    finally:
        db.close()

#edit_calendar_goal 라우터 추가

@router.delete("/delete_calendar_goal/{year}/{month}")
async def delete_calendar_goal(year: int, month: int, request: Request):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))

        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']

        calendar_service.delete_goal(year, month, user_id, db)

        db.commit()

        return JSONResponse(status_code=200, content={"message": "Goal deleted successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the goal"})

    finally:
        db.close()