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
            user_db = user()
            user_db.userid = user_register.userid
            user_db.username = user_register.username
            user_db.email = user_register.email
            user_db.password = user_register.password
            return user_db
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
            if user_service.duplicate_userid(user.userid, db):
                raise UserAlreadyExistsError(f"Userid '{user.userid}' already exists.")
            if user_service.duplicate_email(user.email, db):
                raise UserAlreadyExistsError(f"Email '{user.email}' already exists.")
            db.add(user)
            db.commit()
        except InvalidUserDataError:
            raise
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

    def duplicate_userid(userid: str, db):
        try:
            found_user = user_service.find_user_by_userid(userid, db)
            return found_user is not None
        except UserNotFoundError:
            return False
        except Exception as e:
            raise e

    def duplicate_email(email: str, db):
        try:
            found_user = user_service.find_user_by_email(email, db)
            return found_user is not None
        except UserNotFoundError:
            return False
        except Exception as e:
            raise e

    def edit_user(user_data: user_edit, id: str, db):
        try:
            existing_user = user_service.duplicate_userid(user_data.userid, db)
            if existing_user is True:
                raise UserAlreadyExistsError
            user_service.edit_userid(user_data.userid, id, db)
            user_service.edit_username(user_data.username, id, db)
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
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e

    def delete_user_by_userid(userid: str, db):
        try:
            result = db.query(user).filter(user.userid == userid).delete()
            if result == False:
                raise UserNotFoundError
            db.commit()
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e