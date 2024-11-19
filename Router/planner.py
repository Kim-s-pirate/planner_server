from fastapi.responses import JSONResponse
from Database.database import db, get_db, rollback_to_savepoint
from fastapi import APIRouter
from Service import achievement_service
from Service.planner_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *
from Data.planner import *

router = APIRouter(tags=["planner"], prefix="/planner")

# 성과를 계산하는 코드를 병합
# 교재 진도사항의 변경점을 확인하고 다시 돌려주는 코드가 필요함.

# 삭제를 어떻게 해야하는지
#-> 현재 플래너 등록에 문제가 있어서 swagger가 작동하지 않는 문제 발생
# 주석 처리했음.
# @router.post("/register")
# async def planner_register(request: Request, planner_data: planner_register):
#     with get_db() as db:
#         try:
#             requester_id = AuthorizationService.verify_session(request, db)["id"]
#             planner_data = planner_service.verify_planner(planner_data, requester_id, db)
#             planner_service.register_planner(requester_id, planner_data, db)
#             db.commit()
#             new_progress = achievement_service.get_progress_before_date(planner_data.date, requester_id, db)
#             return JSONResponse(status_code=201, content={"message": new_progress})
#         except Exception as e:
#             return JSONResponse(status_code=500, content={"message": str(e)})

#성과를 보여주는 코드 병합
@router.get("/{date}", summary="플래너 조회", description="해당 날짜의 플래너를 조회한다.", responses={
    200: {"description": "플래너 조회 성공", "content": {"application/json": {"example": {
    "message": {
        "to_do_list": [
            {
                "date": "2024-10-31",
                "user_id": "sfdghsdfghdfasgdafg",
                "title": "수능 완성 과학 문제 풀기",
                "status": True,
                "book_id": "45e124c521344de2df462db1acf0e026e21eaecbabe1eccdb750ae7fc01ca4ab"
            },
            {
                "date": "2024-10-31",
                "user_id": "sfdghsdfghdfasgdafg",
                "title": "수능 완성 국어 문제 풀기",
                "status": False,
                "book_id": "9cc8a56f44ad06c5093bd7cfe9b5f2c5aa9964570025168b28b0989e18309c61"
            },
            {
                "date": "2024-10-31",
                "user_id": "sfdghsdfghdfasgdafg",
                "title": "수특 국어 문제 풀기",
                "status": True,
                "book_id": "b3235d9c5c1e891c15e9931529d1a6be7d2ba030be40885fa70cce163a614e65"
            },
            {
                "date": "2024-10-31",
                "user_id": "sfdghsdfghdfasgdafg",
                "title": "수특 수학 문제 풀기",
                "status": True,
                "book_id": "885bcb7c91b0eb86884de8795c7067002eade23ce008c11d9a2fa7918f6a8176"
            }
        ],
        "time_table_list": [
            {
                "date": "2024-10-31",
                "subject_id": "4162478a991634028468f7cda2f12368479826929fd732a3e342fdc9d6980981",
                "time": [
                    "8:4",
                    "8:1",
                    "8:3",
                    "8:2",
                    "8:5"
                ]
            },
            {
                "date": "2024-10-31",
                "subject_id": "5c5499c7578784c87c1b772f345c23355e2c61b9b5617d12253ea7a67dab567a",
                "time": [
                    "7:4",
                    "7:1",
                    "7:3",
                    "7:2",
                    "7:5"
                ]
            },
            {
                "date": "2024-10-31",
                "subject_id": "9a082f076da7e052705f81358b66f14706c933437b188b60638437f2a244b1d2",
                "time": [
                    "6:2",
                    "6:5",
                    "6:1",
                    "6:4",
                    "6:3"
                ]
            }
        ]
    }
}}}},
    500: {"description": "플래너 조회 실패", "content": {"application/json": {"example": {"message": "Runtime Error"}}}}
})
async def get_planner(request: Request, date: date):
    with get_db() as db:
        try:
            session = AuthorizationService.verify_session(request, db)
            user_id = session['id']
            to_do_list = planner_service.find_to_do_by_date(date, user_id, db)
            time_table_list = planner_service.find_time_table_by_date(date, user_id, db)
            planner = {}
            to_do_list = [planner_service.to_to_do_data(to_do).to_dict() for to_do in to_do_list]
            time_table_list = [planner_service.to_time_table_data(time_table).to_dict() for time_table in time_table_list]
            planner['to_do_list'] = to_do_list
            planner['time_table_list'] = time_table_list
            result = {"user_id": user_id, "date": date.isoformat(), "planner": planner}
            return JSONResponse(status_code=200, content=result)
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Panner find failed"})