from fastapi.responses import JSONResponse
from Database.database import db, get_db, rollback_to_savepoint
from fastapi import APIRouter
from Service.planner_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *
from Data.planner import *

router = APIRouter()

@router.post("/register/planner")
async def planner_register(request: Request, planner_data: planner_register):
    try:
        db = get_db()
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        to_do_list = planner_data.to_do_list
        time_table_list = planner_data.time_table_list
        planner_data = planner_service.verify_planner(planner_data, user_id, db)
        planner_service.register_planner(user_id, planner_data, db)

        planner_service.register_planner_study_time(planner_data.date, user_id, db)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "planner registered successfully"})
    except Exception as e:
        raise e
        rollback_to_savepoint(db)
        
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()
        
@router.get("/planner/{date}")
async def get_planner(request: Request, date: date):
    try:
        db = get_db()
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        planners = planner_service.get_planner(user_id, date, db)
        to_do_list = planner_service.get_to_do_list(user_id, date, db)
        time_table_list = planner_service.get_time_table_list(user_id, date, db)
        planner = planner_service.to_planner_data(planners).dict()
        to_do_list = [planner_service.to_to_do_data(to_do).dict() for to_do in to_do_list]
        time_table_list = [planner_service.to_time_table_data(time_table).dict() for time_table in time_table_list]
        planner['to_do_list'] = to_do_list
        planner['time_table_list'] = time_table_list
        return JSONResponse(status_code=200, content={"message": planner})
    except Exception as e:
        rollback_to_savepoint(db)
        print(e)
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()