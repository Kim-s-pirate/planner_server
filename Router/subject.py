from fastapi.responses import JSONResponse
from Database.database import db
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
    try:
        token = authenticate_user(request)
        subject_data = subject_service.to_subject_db(subject_data, token["userid"])
        subject_service.create_subject(subject_data)
        return JSONResponse(status_code=201, content={"message": "Subject registered successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"message": "Subject registration failed"})
    finally:
        db.commit()

#duplicate_subject

@router.delete("/delete_subject/{subject}")
async def delete_subject(request: Request, subject: str):
    try:
        token = authenticate_user(request)
        found_subject = subject_service.find_subject_by_name(subject)
        if found_subject == None:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        if found_subject.userid != token["userid"]:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this subject"})
        subject_service.delete_subject(subject)
        return JSONResponse(status_code=200, content={"message": "Subject deleted successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"message": "Subject deletion failed"})
    finally:
        db.commit()

@router.get("/subject/{subject}")
async def get_subject(request: Request, subject: str):
    try:
        token = authenticate_user(request)
        found_book = book_service.find_book_by_subject(subject, token["userid"])
        if found_book == None:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        data = [book_service.to_book_data(book).dict() for book in found_book]
        return JSONResponse(status_code=200, content=data)
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Subject retrieval failed"})
    finally:
        db.commit()

@router.get("/edit_subject/{subject}")
async def edit_subject(request: Request, subject: str, new_subject: str):
    try:
        token = authenticate_user(request)
        subject_service.edit_subject_name(subject, new_subject)
        return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
    except SubjectNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": e.__str__()})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Subject edit failed"})
    finally:
        db.commit()