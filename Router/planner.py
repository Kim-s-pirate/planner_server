from fastapi.responses import JSONResponse
from Database.database import db
from fastapi import APIRouter
from Service.planner_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *
from Data.planner import *

router = APIRouter()

@router.post("/planner_register")
async def planner_register(request: Request, planner_data: planner_register):
    try:
        user = AuthorizationService.verify_session(request)
        to_do_list = planner_data.to_do_list
        time_table_list = planner_data.time_table_list
        if to_do_list == [] and time_table_list == []:
            planner_service.delete_planner_by_date(planner_data.date, user)
        if to_do_list == []:
            planner_service.delete_to_do_by_date(planner_data.date, user)
        if time_table_list == []:
            planner_service.delete_time_table_by_date(planner_data.date, user)
        #여기 처리 방식이 잘못됐음
        #어짜피 다시 등록되기 때문에 확인 후 수정
        planner_service.register_planner(user, planner_data)

        planner_service.register_planner_study_time(planner_data.date, user)
        return JSONResponse(status_code=200, content={"message": "planner registered successfully"})
    except Exception as e:
        db.rollback()
        raise e
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.commit()
# @router.get("/get_planner")
# async def get_planner(request: Request, year: str = Query(None), month: str = Query(None), day: str = Query(None)):
#     try:
        