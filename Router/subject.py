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

router = APIRouter()

@router.post("/subject/create")
async def subject_create(request: Request, subject_data: subject_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        subject_data = subject_service.to_subject_db(subject_data, requester_id)
        subject_service.create_subject(subject_data, db)
        return JSONResponse(status_code=201, content={"message": "Subject registered successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except EmptyTitleError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
    except ColorExhaustedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=507, content={"message": "No more colors available in the color set"})
    except SubjectAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Subject already exists"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "Subject registration failed"})
    finally:
        db.close()

@router.get("/subject/check_title_available")
async def check_title_available(request: Request, title: str):
    db = get_db()
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
    finally:
        db.close()

@router.get("/subject/id/{id}")
async def get_subject_by_id(request: Request, id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_id(id, db)
        if not found_subject:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_subject.user_id)
        user = user_service.find_user_by_id(found_subject.user_id, db)
        if not user:
            raise UserNotFoundError
        user = user_service.to_user_data(user).__dict__
        found_subject = subject_service.to_subject_data(found_subject).__dict__
        found_subject['user'] = user
        del found_subject['user_id']
        return JSONResponse(status_code=200, content={"message": found_subject})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        return JSONResponse(status_code=403, content={"message": "You are not authorized to view this subject"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Subject find failed"})
    finally:
        db.close()

# 통합 검색 기능으로 리팩토링
#검색 알고리즘 최적화 필요
@router.get("/search/subject/{title}")
async def get_subject_by_title(request: Request, title: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_title(title, requester_id, db)
        if not found_subject:
            raise SubjectNotFoundError
        user = user_service.find_user_by_id(found_subject.user_id, db)
        if not user:
            raise UserNotFoundError
        user = user_service.to_user_data(user).__dict__
        found_subject = subject_service.to_subject_data(found_subject).__dict__
        found_subject['user'] = user
        del found_subject['user_id']
        return JSONResponse(status_code=200, content={"message": found_subject})
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
    finally:
        db.close()

@router.get("/subject/subject_list")
async def get_subject_list(request: Request):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_user_id(requester_id, db)
        if not found_subject:
            raise SubjectNotFoundError
        user = user_service.find_user_by_id(found_subject[0].user_id, db)
        if not user:
            raise UserNotFoundError
        user = user_service.to_user_data(user).__dict__
        found_subject = [subject_service.to_subject_data(subject).__dict__ for subject in found_subject]
        for subject in found_subject:
            subject['user'] = user
            del subject['user_id']
        return JSONResponse(status_code=200, content={"message": found_subject})
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
    finally:
        db.close()

@router.get("/subject/subject_color/{id}")
async def get_subject_color(request: Request, id: str):
    db = get_db()
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
    finally:
        db.close()

@router.get("/subject/remain_color")
async def remain_color(request: Request):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        remain_color = subject_service.remain_color(requester_id, db)
        return JSONResponse(status_code=200, content={"message": remain_color})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Color find failed"})
    finally:
        db.close()

@router.post("/edit/subject_title/{id}")
async def edit_title(request: Request, new_title: subject_title, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_id(id, db)
        if not found_subject:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_subject.user_id)
        subject_service.edit_title(new_title.title, id, requester_id, db)
        return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject"})
    except EmptyTitleError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
    except SubjectAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Subject already exists"})
    except SubjectNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "Subject edit failed"})
    finally:
        db.close()

@router.post("/edit/subject_color/{id}")
async def edit_color(request: Request, id: str, new_color: subject_color):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_id(id, db)
        if not found_subject:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_subject.user_id)
        subject_service.edit_color(new_color.color, id, requester_id, db)
        return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject"})
    except InvalidSubjectDataError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Invalid subject data"})
    except SubjectNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "Subject edit failed"})
    finally:
        db.close()

@router.delete("/delete/subject/{id}")
async def delete_subject_by_id(request: Request, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
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
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this subject"})
    except SubjectNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "Subject delete failed"})
    finally:
        db.close()


# @router.post("/edit/subject/{id}")
# async def edit_subject_by_id(request: Request, subject_data: subject_edit, id: str):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
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
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=404, content={"message": e.__str__()})
#
#     except SessionIdNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#
#     except Exception as e:
#         rollback_to_savepoint(db)
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
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=404, content={"message": e.__str__()})
#
#     except SessionIdNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#
#     except Exception as e:
#         rollback_to_savepoint(db)
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
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#
#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": "Subject deletion failed"})
#
#     finally:
#         db.close()