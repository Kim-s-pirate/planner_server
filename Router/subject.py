from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import get_db, rollback_to_savepoint
from Database.models import user
from fastapi import APIRouter
from Service import book_service
from Service.subject_service import *
from Service.user_service import *
from Service.log_service import *
from Service.book_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *
from Data.subject import *
from Service.error import *

router = APIRouter(tags=["subject"], prefix="/subject")

@router.post("/create",summary="과목 생성",description="새로운 과목을 생성한다.",responses={
    201: {"description": "과목 생성 성공", "content": {"application/json": {"example": { "message": "Subject registered successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    409: {"description": "제목 공백", "content": {"application/json": {"example": { "message": "Title cannot be blank"}}}},
    507: {"description": "색상 고갈", "content": {"application/json": {"example": { "message": "No more colors available in the color set"}}}},
    409: {"description": "과목 중복", "content": {"application/json": {"example": { "message": "Subject already exists"}}}},
    500: {"description": "과목 생성 실패", "content": {"application/json": {"example": { "message": "Subject registration failed"}}}},
})
async def subject_create(request: Request, subject_data: subject_register):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            subject_data = subject_service.to_subject_db(subject_data, requester_id)
            subject = subject_service.create_subject(subject_data, db)
            subject = subject_service.to_subject_data(subject).__dict__
            del subject['user_id']
            return JSONResponse(status_code=201, content=subject)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except EmptyTitleError as e:
            return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
        except ColorExhaustedError as e:
            return JSONResponse(status_code=507, content={"message": "No more colors available in the color set"})
        except SubjectAlreadyExistsError as e:
            return JSONResponse(status_code=409, content={"message": "Subject already exists"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject registration failed"})

@router.get("/check_title_available",summary="title 중복 확인",description="title이 이미 존재하는지 확인한다.",responses={
    200: {"description": "title 사용 가능", "content": {"application/json": {"example": { "message": "Title is available"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    409: {"description": "과목 중복", "content": {"application/json": {"example": { "message": "Subject already exists"}}}},
    500: {"description": "title 중복 확인 실패", "content": {"application/json": {"example": { "message": "Subject check failed"}}}},
})
async def check_title_available(request: Request, title: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            if subject_service.is_title_exists(title, requester_id, db):
                raise SubjectNotFoundError
            return JSONResponse(status_code=200, content={"message": "Title is available"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=409, content={"message": "Subject already exists"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject check failed"})

@router.get("/id/{id}",summary="subject id 반환",description="해당 subject의 id를 반환한다.",responses={
    200: {"description": "subject id 반환 성공", "content": {"application/json": {"example": { "message": "Subject id returned successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    403: {"description": "권한 없음", "content": {"application/json": {"example": { "message": "You are not authorized to view this subject"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "subject id 반환 실패", "content": {"application/json": {"example": { "message": "Subject id return failed"}}}},
})
async def get_subject_by_id(request: Request, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_subject = subject_service.find_subject_by_id(id, db)
            if not found_subject:
                raise SubjectNotFoundError
            AuthorizationService.check_authorization(requester_id, found_subject.user_id)
            found_subject = subject_service.to_subject_data(found_subject).__dict__
            del found_subject['user_id']
            return JSONResponse(status_code=200, content=found_subject)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this subject"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject find failed"})

# 통합 검색 기능으로 리팩토링
#검색 알고리즘 최적화 필요
@router.get("/search/{title}",summary="과목 검색 기능",description="과목의 제목, 부분제목, 초성, 과목 등으로 검색 가능한 서비스이다.",responses={
    200: {"description": "과목 검색 성공", "content": {"application/json": {"example": { "message": "Subject searched successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    404: {"description": "과목 없음", "content": {"application/json": {"example": { "message": "Subject not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "과목 검색 실패", "content": {"application/json": {"example": { "message": "Subject search failed"}}}},
})
async def get_subject_by_title(request: Request, title: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_subject = subject_service.find_subject_by_title(title, requester_id, db)
            if not found_subject:
                raise SubjectNotFoundError
            AuthorizationService.check_authorization(requester_id, found_subject.user_id)
            found_subject = subject_service.to_subject_data(found_subject).__dict__
            del found_subject['user_id']
            result = {"user_id" : requester_id,"subject" : found_subject}
            return JSONResponse(status_code=200, content=result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject find failed"})

@router.get("/subject_list",summary="과목 리스트 반환",description="해당 사용자의 과목 리스트를 반환한다.",responses={
    200: {"description": "과목 리스트 반환 성공", "content": {"application/json": {"example": { "message": "Subject list returned successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    404: {"description": "과목 없음", "content": {"application/json": {"example": { "message": "Subject not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "과목 리스트 반환 실패", "content": {"application/json": {"example": { "message": "Subject find failed"}}}},
})
async def get_subject_list(request: Request):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_subject = subject_service.find_subject_by_user_id(requester_id, db)
            if not found_subject:
                raise SubjectNotFoundError
            found_subject = [subject_service.to_subject_data(subject).__dict__ for subject in found_subject]
            for subject in found_subject:
                del subject['user_id']
            result = {"user_id" : requester_id,"subject_list" : found_subject}
            return JSONResponse(status_code=200, content=result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject find failed"})

@router.get("/subject_color/{id}",summary="과목 색상 반환",description="해당 id의 과목의 색상을 반환한다.",responses={
    200: {"description": "과목 색상 반환 성공", "content": {"application/json": {"example": { "message": "Subject color returned successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    403: {"description": "권한 없음", "content": {"application/json": {"example": { "message": "You are not authorized to view this subject"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "과목 색상 반환 실패", "content": {"application/json": {"example": { "message": "Color find failed"}}}},
})
async def get_subject_color(request: Request, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_subject = subject_service.find_subject_by_id(id, db)
            if not found_subject:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_subject.user_id)
            return JSONResponse(status_code=200, content={"message": found_subject.color})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this subject"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Color find failed"})

@router.get("/remain_color",summary="사용 가능 색상 반환",description="현재 사용중인 과목 색상을 제외한 사용 가능한 과목 색상을 반환한다.",responses={
    200: {"description": "사용 가능 색상 반환 성공", "content": {"application/json": {"example": { "message": "Remain color returned successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "사용 가능 색상 반환 실패", "content": {"application/json": {"example": { "message": "Color find failed"}}}},
})
async def remain_color(request: Request):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            remain_color = subject_service.remain_color(requester_id, db)
            result = {"user_id" : requester_id,"remain_color" : remain_color}
            return JSONResponse(status_code=200, content=result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Color find failed"})

@router.post("/edit/subject_title/{id}",summary="과목 title 수정",description="주어진 id의 과목 title을 수정한다.",responses={
    200: {"description": "과목 title 수정 성공", "content": {"application/json": {"example": { "message": "Subject edited successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    403: {"description": "권한 없음", "content": {"application/json": {"example": { "message": "You are not authorized to edit this subject"}}}},
    404: {"description": "과목 없음", "content": {"application/json": {"example": { "message": "Subject not found"}}}},
    409: {"description": "title 공백", "content": {"application/json": {"example": { "message": "Title cannot be blank"}}}},
    409: {"description": "과목 중복", "content": {"application/json": {"example": { "message": "Subject already exists"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "과목 title 수정 실패", "content": {"application/json": {"example": { "message": "Subject edit failed"}}}},
})
async def edit_title(request: Request, new_title: subject_title, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_subject = subject_service.find_subject_by_id(id, db)
            if not found_subject:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_subject.user_id)
            subject_service.edit_title(new_title.title, id, requester_id, db)
            return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject"})
        except EmptyTitleError as e:
            return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
        except SubjectAlreadyExistsError as e:
            return JSONResponse(status_code=409, content={"message": "Subject already exists"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject edit failed"})

@router.post("/edit/subject_color/{id}",summary="과목 색상 수정",description="주어진 id의 과목의 색상을 수정한다.",responses={
    200: {"description": "과목 색상 수정 성공", "content": {"application/json": {"example": { "message": "Subject edited successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    403: {"description": "권한 없음", "content": {"application/json": {"example": { "message": "You are not authorized to edit this subject"}}}},
    404: {"description": "과목 없음", "content": {"application/json": {"example": { "message": "Subject not found"}}}},
    400: {"description": "색상 공백", "content": {"application/json": {"example": { "message": "Color cannot be blank"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "과목 색상 수정 실패", "content": {"application/json": {"example": { "message": "Subject edit failed"}}}},
})
async def edit_color(request: Request, id: str, new_color: subject_color):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_subject = subject_service.find_subject_by_id(id, db)
            if not found_subject:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_subject.user_id)
            subject_service.edit_color(new_color.color, id, requester_id, db)
            return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject"})
        except InvalidSubjectDataError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid subject data"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        except ColorAlreadyUsedError as e:
            return JSONResponse(status_code=409, content={"message": "Color already used"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject edit failed"})

@router.delete("/delete/{id}",summary="과목 삭제",description="주어진 id의 과목을 삭제한다.",responses={
    200: {"description": "과목 삭제 성공", "content": {"application/json": {"example": { "message": "Subject deleted successfully"}}}},
    401: {"description": "토큰 없음", "content": {"application/json": {"example": { "message": "Token not found"}}}},
    403: {"description": "권한 없음", "content": {"application/json": {"example": { "message": "You are not authorized to delete this subject"}}}},
    404: {"description": "과목 없음", "content": {"application/json": {"example": { "message": "Subject not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": { "message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": { "message": "Session expired"}}}},
    500: {"description": "과목 삭제 실패", "content": {"application/json": {"example": { "message": "Subject delete failed"}}}},
})
async def delete_subject_by_id(request: Request, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_subject = subject_service.find_subject_by_id(id, db)
            if not found_subject:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_subject.user_id)
            result = subject_service.delete_subject_by_id(id, db)
            if not result:
                raise SubjectNotFoundError
            return JSONResponse(status_code=200, content={"message": "Subject deleted successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this subject"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Subject delete failed"})


# @router.post("/edit/subject/{id}")
# async def edit_subject_by_id(request: Request, subject_data: subject_edit, id: str):
#     db = get_db()
#     try:
#         requester_id = AuthorizationService.verify_session(request, db)["id"]
#         #이쯤에 색깔이 있는지 확인하는 코드가 필요할 듯
#         if requester_id != subject_service.find_subject_by_id(id, db).user_id:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject"})
#         subject_service.edit_subject(subject_data, id, requester_id, db)
#         return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
#     except SessionIdNotFoundError:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError:
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError:
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except SubjectNotFoundError:
#         return JSONResponse(status_code=404, content={"message": "Subject not found"})
#     except:
#         return JSONResponse(status_code=500, content={"message": "There was some error while editing the subject"})
#     finally:
#         db.close()


#@router.post("/edit_subject/{subject}")
#async def edit_subject_name_by_name(request: Request, subject: str, new_subject: str):
#    db = get_db()
#    try:
#        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#        db.execute(text("SAVEPOINT savepoint"))
#
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         subject_service.edit_subject_name_by_name(subject, new_subject, user_id, db)
#
#         db.commit()
#
#         return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
#
#     except SubjectNotFoundError as e:
#         
#         return JSONResponse(status_code=404, content={"message": e.__str__()})
#
#     except SessionIdNotFoundError as e:
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#
#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#
#     except Exception as e:
#         
#         return JSONResponse(status_code=500, content={"message": "Subject edit failed"})
#
#     finally:
#         db.close()

# @router.post("/exchange_color/")
# async def exchange_color(request: Request, subject: str, original_color: str, exchanged_color: str):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         subject_service.exchange_color(user_id, subject, original_color, exchanged_color, db)
#
#         db.commit()
#
#         return JSONResponse(status_code=200, content={"message": "Subject color exchanged successfully"})
#
#     except SubjectNotFoundError as e:
#         
#         return JSONResponse(status_code=404, content={"message": e.__str__()})
#
#     except SessionIdNotFoundError as e:
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#
#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#
#     except Exception as e:
#         
#         return JSONResponse(status_code=500, content={"message": "Subject color edit failed"})
#
#     finally:
#         db.close()

# @router.delete("/delete_subject/{subject}")
# async def delete_subject_by_name(request: Request, subject: str):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         found_subject = subject_service.find_subject_by_name(subject, user_id, db)
#
#         if found_subject == None:
#             return JSONResponse(status_code=404, content={"message": "Subject not found"})
#
#         if found_subject.user_id != user_id:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this subject"})
#
#         subject_service.delete_subject_by_name(subject, user_id, db)
#
#         db.commit()
#
#         return JSONResponse(status_code=200, content={"message": "Subject deleted successfully"})
#
#     except SessionIdNotFoundError as e:
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#
#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#
#     except Exception as e:
#         
#         return JSONResponse(status_code=500, content={"message": "Subject deletion failed"})
#
#     finally:
#         db.close()