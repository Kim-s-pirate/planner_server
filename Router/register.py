from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import db, get_db, rollback_to_savepoint
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *

router = APIRouter()

@router.post("/account/register")
async def register(user_data: user_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        user_data = user_service.to_user_db(user_data)
        user_service.create_user(user_data, db)
        return JSONResponse(status_code=201, content={"message": "User registered successfully"})
    except InvalidUserDataError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Invalid user data"})
    except UserAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "User already exists"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "User registration failed"})
    finally:
        db.close()

@router.get("/account/check_userid_available")
async def check_userid_exists(userid: str = Query(None)):
    db = get_db()
    try:
        if user_service.is_userid_exists(userid, db):
            return JSONResponse(status_code=409, content={"message": "Userid already exists"})
        return JSONResponse(status_code=200, content={"message": "Userid is available"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "User check failed"})
    finally:
        db.close()

@router.get("/account/check_email_exists")
async def check_email_exists(email: str = Query(None)):
    db = get_db()
    try:
        if user_service.is_email_exists(email, db):
            return JSONResponse(status_code=409, content={"message": "Email already exists"})
        return JSONResponse(status_code=200, content={"message": "Email is available"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "User check failed"})
    finally:
        db.close()

@router.post("/edit/user/userid/{id}")
async def edit_user_userid(request: Request, user_data: user_userid, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        AuthorizationService.check_authorization(requester_id, id)
        user_service.edit_userid(user_data.userid, id, db)
        AuthorizationService.modify_session(request, user_data.userid)
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
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
    except InvalidUserDataError:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Userid cannot be empty"})
    except UserNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "User not found"})
    except UserAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "User already exists"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "User edit failed"})
    finally:
        db.close()

@router.post("/edit/user/email/{id}")
async def edit_user_email(request: Request, user_data: user_email, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        AuthorizationService.check_authorization(requester_id, id)
        user_service.edit_email(user_data.email, id, db)
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
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
    except InvalidUserDataError:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Email cannot be empty"})
    except UserNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "User not found"})
    except UserAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "User already exists"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "User edit failed"})
    finally:
        db.close()

@router.post("/edit/user/username/{id}")
async def edit_user_username(request: Request, user_data: user_username, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        AuthorizationService.check_authorization(requester_id, id)
        user_service.edit_username(user_data.username, id, db)
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
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
    except InvalidUserDataError:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Username cannot be empty"})
    except UserNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "User not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "User edit failed"})
    finally:
        db.close()

@router.post("/edit/user/password/{id}")
async def edit_user_password(request: Request, user_data: user_password, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        AuthorizationService.check_authorization(requester_id, id)
        user_service.edit_password(user_data.password, id, db)
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
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
    except InvalidUserDataError:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Password cannot be empty"})
    except UserNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "User not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "User edit failed"})
    finally:
        db.close()

# 서버에서 사용하는 유저 삭제와 회원 탈퇴를 분리해야 함
@router.delete("/delete/user/{id}")
async def delete_user(request: Request, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        AuthorizationService.check_authorization(requester_id, id)
        result = user_service.delete_user_by_id(id, db)
        if not result:
            raise UserNotFoundError
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
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
    except UserNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "User not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "User delete failed"})
    finally:
        db.close()






# @router.delete("/user_delete/{user_id}")
# async def user_delete_by_userid(request: Request, user_id: str):
#     try:
#         db = get_db()
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         userid = AuthorizationService.verify_session(request, db)
#         if userid != user_id:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this user"})
#         user_service.delete_user_by_userid(userid, db)
#         db.commit()
#         return JSONResponse(status_code=200, content={"message": "User deleted successfully"})
#     except SessionIdNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         print(e)
#         return JSONResponse(status_code=500, content={"message": "There was some error while deleting the user"})
#     finally:
#         db.close()

# @router.post("/edit_user/{current_userid}")
# async def edit_user_by_userid(request: Request, user_data: user_edit, current_userid: str):
#     try:
#         db = get_db()
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         userid = AuthorizationService.verify_session(request, db)
#         if userid != current_userid:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
#         found_user = user_service.find_user_by_userid(current_userid, db)
#         if found_user == None:
#             return JSONResponse(status_code=404, content={"message": "User not found"})
#         user_service.edit_user(user_data, current_userid, db)
#         AuthorizationService.modify_session(request, current_userid)
#         db.commit()
#         return JSONResponse(status_code=200, content={"message": "User edited successfully"})
#     except SessionIdNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         print(e)
#         return JSONResponse(status_code=500, content={"message": "There was some error while editing the user"})
#     finally:
#         db.close()
