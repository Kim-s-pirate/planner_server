from Database.models import user
from Data.user import *
from Database.database import db
from Service.error import *

class user_service:
    def to_user_db(user_register: user_register): #
        try:
            return user(
                userid=user_register.userid,
                username=user_register.username,
                email=user_register.email,
                password=user_register.password
            )
        except:
            raise InvalidUserDataError

    def to_user_data(user_entity: user): #
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

    def find_user_by_id(id: int, db): #
        return db.query(user).filter(user.id == id).first()

    def find_user_by_userid(userid: str, db): #
        return db.query(user).filter(user.userid == userid).first()

    def find_user_by_email(email: str, db): #
        return db.query(user).filter(user.email == email).first()

    def is_userid_exists(userid: str, db): #
        found_user = user_service.find_user_by_userid(userid, db)
        if found_user == None:
            return False
        return True

    def is_email_exists(email: str, db): #
        found_user = user_service.find_user_by_email(email, db)
        if found_user == None:
            return False
        return True

    def edit_user(user_data: user_edit, id: str, db): #
        try:
            if user_service.is_userid_exists(user_data.userid, db):
                raise UserAlreadyExistsError
            user_service.edit_userid(user_data.userid, id, db)
            user_service.edit_username(user_data.username, id, db)
        except Exception as e:
            raise e

    def edit_userid(new_userid: str, id: str, db): #
        try:
            found_user = user_service.find_user_by_id(id, db)
            if not found_user:
                raise UserNotFoundError
            found_user.userid = new_userid
        except Exception as e:
            raise e

    def edit_username(new_username: str, id: str, db): #
        try:
            found_user = user_service.find_user_by_id(id, db)
            if not found_user:
                raise UserNotFoundError
            found_user.username = new_username
        except Exception as e:
            raise e

    def edit_email(new_email: str, id: str, db): #
        try:
            found_user = user_service.find_user_by_id(id, db)
            if not found_user:
                raise UserNotFoundError
            found_user.email = new_email
        except Exception as e:
            raise e

    def edit_password(new_password: str, id: str, db): #
        try:
            found_user = user_service.find_user_by_id(id, db)
            if not found_user:
                raise UserNotFoundError
            found_user.password = new_password
        except Exception as e:
            raise e

    def delete_user_by_id(id: str, db): #
        try:
            result = db.query(user).filter(user.id == id).delete()
            if result == False:
                raise UserNotFoundError
        except Exception as e:
            raise e

    def delete_user_by_userid(userid: str, db): #
        try:
            result = db.query(user).filter(user.userid == userid).delete()
            if result == False:
                raise UserNotFoundError
        except Exception as e:
            raise e