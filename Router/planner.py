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

# 성과를 계산하는 코드를 병합
# 교재 진도사항의 변경점을 확인하고 다시 돌려주는 코드가 필요함.

# 삭제를 어떻게 해야하는지
# 빈 데이터가 들어오면 값을 비교하지 말고 삭제를 한 후 넘어가는 식으로 코드를 작성 -> register에서 해결
#-> 현재 플래너 등록에 문제가 있어서 swagger가 작동하지 않는 문제 발생
# 주석 처리했음.
# @router.post("/register/planner")
# async def planner_register(request: Request, planner_data: planner_register):
#     try:
#         db = get_db()
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         planner_data = planner_service.verify_planner(planner_data, user_id, db)
#         planner_service.register_planner(user_id, planner_data, db)
#         db.commit()
#         return JSONResponse(status_code=201, content={"message": "planner registered successfully"})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": str(e)})
#     finally:
#         db.close()

#성과를 보여주는 코드 병합
@router.get("/planner/{date}")
async def get_planner(request: Request, date: date):
    try:
        db = get_db()
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        to_do_list = planner_service.find_to_do_by_date(user_id, date, db)
        time_table_list = planner_service.find_time_table_by_date(user_id, date, db)
        planner = {}
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