from typing import List
from fastapi.responses import JSONResponse
from Data.schedule import day_schedule, day_schedule_register
from Data.calendar import calendar_goal_register, calendar_goal
from Database.database import db
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
load_dotenv("../.env")
secret = os.getenv("secret")

@router.post("/register_schedule")
async def register_schedule(schedule_data: day_schedule_register, request: Request):
    try:
        token = authenticate_user(request)

        if schedule_data.schedule == None:
            calendar_service.delete_schedule(schedule_data.date, token["userid"])
        else:
            calendar_service.register_schedule(schedule_data, token["userid"])
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Schedule registered successfully"})
    
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "There was some error while registering the schedule"})
    finally:
        db.commit()

@router.get("/get_month_schedule")
async def get_schedule(request: Request, year: str = Query(None), month: str = Query(None)):
    try:
        token = authenticate_user(request)
        schedule = calendar_service.get_month_schedule(year, month, token["userid"])
        schedule = [calendar_service.to_schedule_data(s).__dict__ for s in schedule]
        for s in schedule:
            if 'date' in s and s['date']:
                s['date'] = s['date'].isoformat()
        return JSONResponse(status_code=200, content={"schedule": schedule})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "There was some error while getting the schedule"})
    finally:
        db.commit()

@router.post("/register_calendar_goal")
async def register_calendar_goal(goal_data: calendar_goal_register, request: Request):
    try:
        token = authenticate_user(request)
        if goal_data.month_goal == None and goal_data.week_goal == None:
            calendar_service.delete_goal(goal_data.year, goal_data.month, token["userid"])
        else:
            calendar_service.register_goal(goal_data, token["userid"])
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Goal registered successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "There was some error while registering the goal"})
    finally:
        db.commit()

@router.delete("/delete_calendar_goal/{year}/{month}")
async def delete_calendar_goal(year: int, month: int, request: Request):
    try:
        token = authenticate_user(request)
        calendar_service.delete_goal(year, month, token["userid"])
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Goal deleted successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the goal"})
    finally:
        db.commit()

#edit_calendar_goal 라우터 추가