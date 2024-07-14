from typing import List
from fastapi.responses import JSONResponse
from Data.schedule import day_schedule, day_schedule_register
from Data.calender import calendar_goal, calendar_goal_register
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
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=400, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=400, content={"message": "Token verification failed"})
        token = decode_token(token)

        if schedule_data.schedule == None:
            calendar_service.delete_schedule(schedule_data.date, token["userid"])
        else:
            calendar_service.register_schedule(schedule_data, token["userid"])
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Schedule registered successfully"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=409, content={"message": "There was some error while registering the schedule"})
    finally:
        db.commit()

@router.get("/get_month_schedule")
async def get_schedule(request: Request, year: str = Query(None), month: str = Query(None)):
    try:
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=400, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=400, content={"message": "Token verification failed"})
        token = decode_token(token)
        schedule = calendar_service.get_month_schedule(year, month, token["userid"])
        schedule = [calendar_service.to_schedule_data(s).__dict__ for s in schedule]
        for s in schedule:
            if 'date' in s and s['date']:
                s['date'] = s['date'].isoformat()
        return JSONResponse(status_code=200, content={"schedule": schedule})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=409, content={"message": "There was some error while getting the schedule"})
    finally:
        db.commit()

@router.get("/register_goal")
async def register_goal(goal_data: week_goal_register, request: Request):
    try:
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=400, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=400, content={"message": "Token verification failed"})
        token = decode_token(token)
        if goal_data.goal == None:
            calendar_service.delete_goal(goal_data.date, token["userid"])
        else:
            calendar_service.register_goal(goal_data, token["userid"])
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Goal registered successfully"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=409, content={"message": "There was some error while registering the goal"})
    finally:
        db.commit()

@router.post("/register_calendar_goal")
async def register_calendar_goal(goal_data: week_goal_register, request: Request):
    try:
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=400, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=400, content={"message": "Token verification failed"})
        token = decode_token(token)
        if goal_data.month_goal == None and goal_data.week_goal == None:
            calendar_service.delete_goal(goal_data.year, goal_data.month, token["userid"])
        else:
            calendar_service.register_goal(goal_data.year, goal_data.month, token["userid"])
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Goal registered successfully"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=409, content={"message": "There was some error while registering the goal"})
    finally:
        db.commit()