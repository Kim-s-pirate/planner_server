from Database.models import user
from Data.user import *
from Database.database import db

class UserNotFoundError(Exception):
    def __init__(self, message="User not found."):
        self.message = message
        super().__init__(self.message)

class UserAlreadyExistsError(Exception):
    def __init__(self, message="User already exists."):
        self.message = message
        super().__init__(self.message)

class InvalidUserDataError(Exception):
    def __init__(self, message="Invalid user data."):
        self.message = message
        super().__init__(self.message)


class DatabaseCommitError(Exception):
    def __init__(self, message="Database commit error occurred."):
        self.message = message
        super().__init__(self.message)


class UserUpdateError(Exception):
    def __init__(self, message="Failed to update user."):
        self.message = message
        super().__init__(self.message)

class user_service:
    def to_user_db(user_register: user_register):
        try:
            return user(
                userid=user_register.userid,
                username=user_register.username,
                email=user_register.email,
                password=user_register.password
            )
        except:
            raise InvalidUserDataError

    def to_user_data(user_entity: user):
        return user_data(
            id=user_entity.id,
            userid=user_entity.userid,
            username=user_entity.username,
            email=user_entity.email
        )
    #이 부분 비밀번호가 들어가기 때문에 수정해야함

    def create_user(user: user, db):
        try:
            user_service.check_userid_exists(user.userid, db)
            user_service.check_email_exists(user.email, db)
            db.add(user)
            db.commit()
        except UserAlreadyExistsError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e

    def find_user_by_id(id: int, db):
        user_from_id = db.query(user).filter(user.id == id).first()
        if not user_from_id:
            raise UserNotFoundError
        return user_from_id

    def find_user_by_userid(userid: str, db):
        user_from_userid = db.query(user).filter(user.userid == userid).first()
        if not user_from_userid:
            raise UserNotFoundError
        return user_from_userid

    def find_user_by_email(email: str, db):
        user_from_email = db.query(user).filter(user.email == email).first()
        if not user_from_email:
            raise UserNotFoundError
        return user_from_email

    def check_userid_exists(userid: str, db):
        try:
            user_service.find_user_by_userid(userid, db)
            raise UserAlreadyExistsError
        except UserNotFoundError:
            pass
        except UserAlreadyExistsError:
            raise UserAlreadyExistsError(f"Userid '{userid}' already exists.")
        except Exception as e:
            raise e

    def check_email_exists(email: str, db):
        try:
            user_service.find_user_by_email(email, db)
            raise UserAlreadyExistsError
        except UserNotFoundError:
            pass
        except UserAlreadyExistsError:
            raise UserAlreadyExistsError(f"Userid '{email}' already exists.")
        except Exception as e:
            raise e

    def edit_user(user_data: user_edit, id: str, db):
        try:
            user_service.check_userid_exists(user_data.userid, db)
            user_service.edit_userid(user_data.userid, id, db)
            user_service.edit_username(user_data.username, id, db)
        except UserAlreadyExistsError:
            raise
        except UserNotFoundError:
            raise
        except Exception as e:
            raise UserUpdateError from e

    def edit_userid(new_userid: str, id: str, db):
        try:
            found_user = user_service.find_user_by_id(id, db)
            found_user.userid = new_userid
            db.commit()
        except UserNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise UserUpdateError from e

    def edit_username(new_username: str, id: str, db):
        try:
            found_user = user_service.find_user_by_id(id, db)
            found_user.username = new_username
            db.commit()
        except UserNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise UserUpdateError from e

    def edit_email(new_email: str, id: str, db):
        try:
            found_user = user_service.find_user_by_id(id, db)
            found_user.email = new_email
            db.commit()
        except UserNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise UserUpdateError from e

    def edit_password(new_password: str, id: str, db):
        try:
            found_user = user_service.find_user_by_id(id, db)
            found_user.password = new_password
            db.commit()
        except UserNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise UserUpdateError from e

    def delete_user_by_id(id: str, db):
        try:
            result = db.query(user).filter(user.id == id).delete()
            if result == False:
                raise UserNotFoundError
            db.commit()
        except UserNotFoundError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e

    def delete_user_by_userid(userid: str, db):
        try:
            result = db.query(user).filter(user.userid == userid).delete()
            if result == False:
                raise UserNotFoundError
            db.commit()
        except UserNotFoundError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e