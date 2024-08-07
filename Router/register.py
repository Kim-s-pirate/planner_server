from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import get_db, rollback_to_savepoint
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *

router = APIRouter()

@router.post("/register")
async def register(user_data: user_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))

        if user_service.find_user_by_email(user_data.email, db) != None:
            return JSONResponse(status_code=409, content={"message": "Email already exists"})

        if user_service.find_user_by_userid(user_data.userid, db) != None:
            return JSONResponse(status_code=409, content={"message": "User already exists"})

        user_data = user_service.to_user_db(user_data)
        user_service.create_user(user_data, db)

        db.commit()

        return JSONResponse(status_code=201, content={"message": "User registered successfully"})

    except:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "User registration failed"})

    finally:
        db.close()
    
@router.get("/duplicate_id")
async def duplicate_id(userid: str):
    db = get_db()
    try:
        if user_service.find_user_by_userid(userid, db) == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        return JSONResponse(status_code=409, content={"message": "User already exists"})

    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the user"})

    finally:
        db.close()
    
@router.get("/duplicate_email")
async def duplicate_email(email: str):
    db = get_db()
    try:
        found_user = user_service.find_user_by_email(email, db)

        if found_user == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        return JSONResponse(status_code=409, content={"message": "User already exists"})

    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the user"})

    finally:
        db.close()

@router.post("/edit_user/{current_userid}")
async def edit_user(request: Request, user_data: user_edit, current_userid: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))

        userid = AuthorizationService.verify_session(request, db)

        if userid != current_userid:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})

        found_user = user_service.find_user_by_userid(current_userid, db)

        if found_user == None:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        user_service.edit_user(user_data, current_userid, db)

        AuthorizationService.modify_session(request, current_userid)

        db.commit()

        return JSONResponse(status_code=200, content={"message": "User edited successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})

    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while editing the user"})

    finally:
        db.close()

@router.delete("/user_delete/{user_id}")
async def user_delete(request: Request, user_id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))

        userid = AuthorizationService.verify_session(request, db)

        if userid != user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this user"})

        user_service.delete_user(userid, db)

        db.commit()

        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})

    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the user"})

    finally:
        db.close()