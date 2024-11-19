from typing_extensions import deprecated
from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import db, get_db, rollback_to_savepoint
from Data.user import *
from Database.models import user
from fastapi import APIRouter
from Service.email_service import email_service
from Service.user_service import *
from Service.log_service import *
from starlette.status import *
from fastapi import Query, Request
from Service.authorization_service import *
from Service.email_service import *
from Data.oauth import *

router = APIRouter(tags=["account"], prefix="/account")

@router.post("/register",summary="회원가입",description="회원정보와 state를 통해 회원가입한다.",responses={
    201: {"description": "회원가입 성공", "content": {"application/json": {"example": {"message": "User registered successfully"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Email cannot be blank"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Email cannot contain spaces"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Userid cannot be blank"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Userid cannot contain spaces"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Userid must be between 3 and 20 characters long"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Username cannot be blank"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Password cannot be blank"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Password cannot contain spaces"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Password must be between 3 and 20 characters long"}}}},
    400: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "Invalid user data"}}}},
    409: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "User already exists"}}}},
    500: {"description": "회원가입 실패", "content": {"application/json": {"example": {"message": "User registration failed"}}}},
}
)
async def register(user_data: user_register):
    with get_db() as db:
        try:
            if email_service.is_valid_email(user_data.email) is False:
                raise InvalidEmailError
            state=user_data.state
            found_state = email_service.find_state(user_data.email, db)

            if state == found_state.state and user_data.email == found_state.email:
                pass
            elif found_state is None:
                raise StateNotFoundError
            elif state != found_state.state:
                raise StateMismatchError
            elif user_data.email != found_state.email:
                raise EmailMismatchError
            user_service.register_form_validation(user_data)
            user_data = user_service.to_user_db(user_data)
            user_service.create_user(user_data, db)
            return JSONResponse(status_code=201, content={"message": "User registered successfully"})
        except EmptyEmailError as e:
            return JSONResponse(status_code=400, content={"message": "Email cannot be blank"})
        except InvalidEmailError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid email"})
        except EmailContainsSpacesError as e:
            return JSONResponse(status_code=400, content={"message": "Email cannot contain spaces"})
        except EmptyUseridError as e:
            return JSONResponse(status_code=400, content={"message": "Userid cannot be blank"})
        except UseridContainsSpacesError as e:
            return JSONResponse(status_code=400, content={"message": "Userid cannot contain spaces"})
        except InappositeUseridLengthError as e:
            return JSONResponse(status_code=400, content={"message": "Userid must be between 3 and 20 characters long"})
        except EmptyUsernameError as e:
            return JSONResponse(status_code=400, content={"message": "Username cannot be blank"})
        except EmptyPasswordError as e:
            return JSONResponse(status_code=400, content={"message": "Password cannot be blank"})
        except PasswordContainsSpacesError as e:
            return JSONResponse(status_code=400, content={"message": "Password cannot contain spaces"})
        except InappositePasswordLengthError as e:
            return JSONResponse(status_code=400, content={"message": "Password must be between 3 and 20 characters long"})
        except InvalidUserDataError as e:
            return JSONResponse(status_code=400, content={"message": "Invalid user data"})
        except UserAlreadyExistsError as e:
            return JSONResponse(status_code=409, content={"message": "User already exists"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "User registration failed"})

@router.get("/check_userid_available",summary="userid 중복 확인",description="userid가 이미 존재하는지 확인한다.",responses={
    200: {"description": "userid 중복 확인 성공", "content": {"application/json": {"example": {"message": "Userid is available"}}}},
    409: {"description": "userid 중복 확인 실패", "content": {"application/json": {"example": {"message": "Userid already exists"}}}},
    500: {"description": "userid 중복 확인 실패", "content": {"application/json": {"example": {"message": "User check failed"}}}},
})
async def check_userid_available(userid: str):
    with get_db() as db:
        try:
            if user_service.is_userid_exists(userid, db):
                raise UserAlreadyExistsError
            return JSONResponse(status_code=200, content={"message": "Userid is available"})
        except UserAlreadyExistsError:
            return JSONResponse(status_code=409, content={"message": "Userid already exists"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "User check failed"})

@router.get("/check_email_available",summary="email 중복 확인",description="email이 이미 존재하는지 확인한다.",responses={
    200: {"description": "email 중복 확인 성공", "content": {"application/json": {"example": {"message": "Email is available"}}}},
    409: {"description": "email 중복 확인 실패", "content": {"application/json": {"example": {"message": "Email already exists"}}}},
    500: {"description": "email 중복 확인 실패", "content": {"application/json": {"example": {"message": "User check failed"}}}},
})
async def check_email_available(email: str):
    with get_db() as db:
        try:
            if email_service.is_valid_email(email) is False:
                raise InvalidEmailError
            if user_service.is_email_exists(email, db):
                raise UserAlreadyExistsError
            return JSONResponse(status_code=200, content={"message": "Email is available"})
        except UserAlreadyExistsError:
            return JSONResponse(status_code=409, content={"message": "Email already exists"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "User check failed"})
        except InvalidEmailError:
            return JSONResponse(status_code=400, content={"message": "Invalid email"})

@router.post("/edit/userid/{id}",summary="userid 수정",description="userid를 주어진 정보로 수정한다.",responses={
    200: {"description": "userid 수정 성공", "content": {"application/json": {"example": {"message": "User edited successfully"}}}},
    400: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "Userid cannot be empty"}}}},
    401: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    403: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "You are not authorized to edit this user"}}}},
    404: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "User not found"}}}},
    409: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "User already exists"}}}},
    417: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "userid 수정 실패", "content": {"application/json": {"example": {"message": "User edit failed"}}}},
})
async def edit_userid(request: Request, user_data: user_userid, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            AuthorizationService.check_authorization(requester_id, id)
            user_service.edit_userid(user_data.userid, id, db)
            AuthorizationService.modify_session(request, user_data.userid)
            return JSONResponse(status_code=200, content={"message": "User edited successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
        except InvalidUserDataError:
            return JSONResponse(status_code=400, content={"message": "Userid cannot be empty"})
        except UserNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        except UserAlreadyExistsError as e:
            return JSONResponse(status_code=409, content={"message": "User already exists"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "User edit failed"})

@router.post("/edit/username/{id}",summary="username 수정",description="username을 주어진 정보로 수정한다.",responses={
    200: {"description": "username 수정 성공", "content": {"application/json": {"example": {"message": "User edited successfully"}}}},
    400: {"description": "username 수정 실패", "content": {"application/json": {"example": {"message": "Username cannot be empty"}}}},
    401: {"description": "username 수정 실패", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    403: {"description": "username 수정 실패", "content": {"application/json": {"example": {"message": "You are not authorized to edit this user"}}}},
    404: {"description": "username 수정 실패", "content": {"application/json": {"example": {"message": "User not found"}}}},
    417: {"description": "username 수정 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "username 수정 실패", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "username 수정 실패", "content": {"application/json": {"example": {"message": "User edit failed"}}}},
})
async def edit_username(request: Request, user_data: user_username, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            AuthorizationService.check_authorization(requester_id, id)
            user_service.edit_username(user_data.username, id, db)
            return JSONResponse(status_code=200, content={"message": "User edited successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
        except InvalidUserDataError:
            return JSONResponse(status_code=400, content={"message": "Username cannot be empty"})
        except UserNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "User edit failed"})

#username과 id를 동시에 수정하는 코드 작성 바람

@router.post("/edit/password/{id}",summary="password 수정",description="password를 주어진 정보로 수정한다.",responses={
    200: {"description": "password 수정 성공", "content": {"application/json": {"example": {"message": "User edited successfully"}}}},
    400: {"description": "password 수정 실패", "content": {"application/json": {"example": {"message": "Password cannot be empty"}}}},
    401: {"description": "password 수정 실패", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    403: {"description": "password 수정 실패", "content": {"application/json": {"example": {"message": "You are not authorized to edit this user"}}}},
    404: {"description": "password 수정 실패", "content": {"application/json": {"example": {"message": "User not found"}}}},
    417: {"description": "password 수정 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "password 수정 실패", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "password 수정 실패", "content": {"application/json": {"example": {"message": "User edit failed"}}}},
})
async def edit_password(request: Request, user_data: user_password, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            AuthorizationService.check_authorization(requester_id, id)
            user_service.edit_password(user_data.password, id, db)
            return JSONResponse(status_code=200, content={"message": "User edited successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
        except InvalidUserDataError:
            return JSONResponse(status_code=400, content={"message": "Password cannot be empty"})
        except UserNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "User edit failed"})

# 서버에서 사용하는 유저 삭제와 회원 탈퇴를 분리해야 함
@router.delete("/delete/{id}",summary="user 삭제",description="주어진 id를 가진 user를 삭제한다.",responses={
    200: {"description": "user 삭제 성공", "content": {"application/json": {"example": {"message": "User deleted successfully"}}}},
    401: {"description": "user 삭제 실패", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    403: {"description": "user 삭제 실패", "content": {"application/json": {"example": {"message": "You are not authorized to edit this user"}}}},
    404: {"description": "user 삭제 실패", "content": {"application/json": {"example": {"message": "User not found"}}}},
    417: {"description": "user 삭제 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "user 삭제 실패", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    500: {"description": "user 삭제 실패", "content": {"application/json": {"example": {"message": "User delete failed"}}}},
})
async def delete_user(request: Request, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            AuthorizationService.check_authorization(requester_id, id)
            result = user_service.delete_user_by_id(id, db)
            if not result:
                raise UserNotFoundError
            AuthorizationService.delete_session(request)
            return JSONResponse(status_code=200, content={"message": "User deleted successfully"})
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
        except UserNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "User delete failed"})

# @router.post("/edit/user/email/{id}")
# async def edit_user_email(request: Request, user_data: user_email, id: str):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))
#         requester_id = AuthorizationService.verify_session(request, db)["id"]
#         AuthorizationService.check_authorization(requester_id, id)
#         user_service.edit_email(user_data.email, id, db)
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
#     except UnauthorizedError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this user"})
#     except InvalidUserDataError:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=400, content={"message": "Email cannot be empty"})
#     except UserNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=404, content={"message": "User not found"})
#     except UserAlreadyExistsError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=409, content={"message": "User already exists"})
#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": "User edit failed"})
#     finally:
#         db.close()

# @router.post("/account/oauth2/naver/register")
# async def oauth_register(request: Request, naver_data: naver_data, oauth_user_data: oauth_register):
#     db = get_db()
#     try:
#         userid=oauth_user_data.userid
#         username=oauth_user_data.username
#         user_service.register_oauth_form_validation(oauth_user_data)
#         user_service.register_oauth_user(naver_data, oauth_user_data, db)

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
