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

router = APIRouter()

@router.post("/subject_register")
async def subject_register(request: Request, subject_data: subject_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        subject_data = subject_service.to_subject_db(subject_data, requester_id)
        subject_service.create_subject(subject_data, db)
        return JSONResponse(status_code=201, content={"message": "Subject registered successfully"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except ColorExhaustedError as e:
        return JSONResponse(status_code=507, content={"message": e.message})
    except SubjectAlreadyExistsError as e:
        return JSONResponse(status_code=409, content={"message": e.message})
    except:
        return JSONResponse(status_code=500, content={"message": "Subject registration failed"})
    finally:
        db.close()

@router.get("/check_title_exists/{title}")
async def check_title_exists(request: Request, title: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        subject_service.check_title_exists(title, requester_id, db)
        return JSONResponse(status_code=200, content={"message": "Title is available"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectAlreadyExistsError as e:
        return JSONResponse(status_code=409, content={"message": e.message})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the subject"})
    finally:
        db.close()

@router.get("/subject/{id}")
async def get_subject_by_id(request: Request, id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_id(id, db)
        if requester_id != found_subject.user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this subject"})
        subject_data = subject_service.to_subject_data(found_subject)
        return JSONResponse(status_code=200, content={"message": subject_data.__dict__})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the subject"})
    finally:
        db.close()

@router.get("/subject/{title}")
async def get_subject_by_title(request: Request, title: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_title(title, requester_id, db)
        subject_data = subject_service.to_subject_data(found_subject)
        return JSONResponse(status_code=200, content={"message": subject_data.__dict__})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the subject"})
    finally:
        db.close()

@router.get("/subject_list")
async def get_subject_list(request: Request):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_subject = subject_service.find_subject_by_user_id(requester_id, db)
        ####################
        data = {"userid": userid, "subjects": [subject_service.to_subject_data(subject).title for subject in found_subject]}
        return JSONResponse(status_code=200, content={"message": data})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the subject"})
    finally:
        db.close()

@router.get("/subject_color/{id}")
async def subject_color(request: Request, id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)
        found_subject = subject_service.find_subject_by_id(id, db)
        if requester_id != found_subject.user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this subject"})
        return JSONResponse(status_code=200, content={"message": found_subject.color})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the color"})
    finally:
        db.close()

@router.get("/remain_color")
async def remain_color(request: Request):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        remain_color = subject_service.remain_color(requester_id, db)
        return JSONResponse(status_code=200, content={"message": remain_color})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the color"})
    finally:
        db.close()

@router.post("/edit_subject/{id}")
async def edit_subject_by_id(request: Request, subject_data: subject_edit, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        #########
        if requester_id != subject_service.find_subject_by_id(id, db).user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject"})
        subject_service.edit_subject(subject_data, id, requester_id, db)
        return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while editing the subject"})
    finally:
        db.close()

@router.post("/edit_color/{id}")
async def edit_color(request: Request, id: str, new_color: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        requester_id = AuthorizationService.verify_session(request, db)
        if requester_id != subject_service.find_subject_by_id(id, db).user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject"})
        subject_service.edit_subject_color(new_color, id, db)
        return JSONResponse(status_code=200, content={"message": "Subject color edited successfully"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while editing the subject"})
    finally:
        db.close()

@router.delete("/delete_subject/{id}")
async def delete_subject_by_id(request: Request, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        requester_id = AuthorizationService.verify_session(request, db)
        if requester_id != subject_service.find_subject_by_id(id, db).user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this subject"})
        subject_service.delete_subject_by_id(id, db)
        return JSONResponse(status_code=200, content={"message": "Subject deleted successfully"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the subject"})
    finally:
        db.close()

























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