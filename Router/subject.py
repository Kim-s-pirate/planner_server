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
        userid = AuthorizationService.verify_session(request)
        subject_data = subject_service.to_subject_db(subject_data, userid)
        subject_service.create_subject(subject_data)
        return JSONResponse(status_code=201, content={"message": "Subject registered successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except IndexError as e:
        return JSONResponse(status_code=500, content={"message": "Maximum number of subjects reached"}) #해당 반환에 대한 status code 논의가 필요함
    except SubjectAlreadyExistsError as e:
        return JSONResponse(status_code=500, content={"message": "Subject already exists"}) #해당 반환에 대한 status code 논의가 필요함
    except Exception as e:
        db.rollback()
        raise e
        return JSONResponse(status_code=500, content={"message": "Subject registration failed"})
    finally:
        db.commit()

#과목의 색을 변경할 수 있는 엔드 포인트 필요함.
#과목끼리 색을 교환할 수 있는 엔드 포인트 필요함.

#duplicate_subject
@router.get("/duplicate_subject")
async def duplicate_subject(request: Request, subject: str):
    try:
        userid = AuthorizationService.verify_session(request)
        found_subject = subject_service.find_subject_by_name(subject, userid)
        if found_subject == None:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})# modify?? : subject can be created
        return JSONResponse(status_code=409, content={"message": f"Subject '{subject}' already exists"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the subject"})

@router.delete("/delete_subject/{subject}")
async def delete_subject(request: Request, subject: str):
    try:
        userid = AuthorizationService.verify_session(request)
        found_subject = subject_service.find_subject_by_name(subject, userid)
        if found_subject == None:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        if found_subject.userid != userid:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this subject"})
        subject_service.delete_subject(subject)
        return JSONResponse(status_code=200, content={"message": "Subject deleted successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"message": "Subject deletion failed"})
    finally:
        db.commit()

@router.get("/subject/{subject}") #이거 이름 수정하고 과목에 대한 엔드포인트로 변경
async def get_subject(request: Request, subject: str):
    try:
        userid = AuthorizationService.verify_session(request)
        found_subject = subject_service.find_subject_by_name(subject, userid)
        if found_subject == []:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        data = subject_service.to_subject_data(found_subject)
        return JSONResponse(status_code=200, content=data.__dict__)
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Subject retrieval failed"})
    finally:
        db.commit()

@router.post("/edit_subject/{subject}")
async def edit_subject(request: Request, subject: str, new_subject: str):
    try:
        userid = AuthorizationService.verify_session(request)
        subject_service.edit_subject_name(subject, new_subject, userid)
        return JSONResponse(status_code=200, content={"message": "Subject edited successfully"})
    except SubjectNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": e.__str__()})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Subject edit failed"})
    finally:
        db.commit()

@router.get("/subject_list")
async def get_subject_list(request: Request):
    try:
        userid = AuthorizationService.verify_session(request)
        found_subject = subject_service.find_subject_by_userid(userid)
        if found_subject == None:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        data = {"userid": userid, "subjects": [subject_service.to_subject_data(subject).subject for subject in found_subject]}
        return JSONResponse(status_code=200, content=data)
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Subject list retrieval failed"})
    finally:
        db.commit()