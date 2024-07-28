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
        userid = AuthorizationService.verify_session(request)
        if planner_data.to_do_list == [] and planner_data.time_table_list == []:
            planner_service.delete_planner(planner_data.date, userid)
        else:
            planner_service.subject_validator(planner_data, userid)
            planner_data = planner_service.to_planner_db(planner_data, userid)
            planner_service.register_planner(planner_data)
        return JSONResponse(status_code=200, content={"message": "Planner registered successfully"})
    #여기서 날리는 200에 대해서 201과 200에 대한 차이는 프론트랑 얘기해보기
    except SubjectNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        raise e
        return JSONResponse(status_code=500, content={"message": "Planner registration failed"})
    finally:
        db.commit()

@router.get("/get_planner")
async def get_planner(request: Request, year: str = Query(None), month: str = Query(None), day: str = Query(None)):
    try:
        userid = AuthorizationService.verify_session(request)
        date = datetime.date(datetime(int(year), int(month), int(day)))
        planner = planner_service.find_planner_by_date(date, userid)
        planner = planner_service.to_planner_data(planner)
        planner = planner_service.planner_to_dict(planner)
        return JSONResponse(status_code=200, content={"planner": planner})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while getting the planner"})
    finally:
        db.commit()