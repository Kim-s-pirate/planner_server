from Database.models import user
from Data.user import *
from Database.database import db
from Service.error import *

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
            if user_service.is_userid_exists(user.userid, db):
                raise UserAlreadyExistsError
            if user_service.is_email_exists(user.email, db):
                raise UserAlreadyExistsError
            db.add(user)
            db.commit()
        except Exception as e:
            raise e

    def find_user_by_id(id: str, db):
        return db.query(user).filter(user.id == id).first()

    def find_user_by_userid(userid: str, db):
        return db.query(user).filter(user.userid == userid).first()

    def find_another_user_by_userid(userid: str, id: str, db):
        return db.query(user).filter(user.userid == userid, user.id != id).first()

    def find_user_by_email(email: str, db):
        return db.query(user).filter(user.email == email).first()

    def find_another_user_by_email(email: str, id: str, db):
        return db.query(user).filter(user.email == email, user.id != id).first()

    def is_userid_exists(userid: str, db):
        return db.query(user).filter(user.userid == userid).first() is not None

    def is_email_exists(email: str, db):
        return db.query(user).filter(user.email == email).first() is not None

    def edit_userid(new_userid: str, id: str, db):
        if new_userid == "" or new_userid == None:
            raise InvalidUserDataError
        found_user = user_service.find_user_by_id(id, db)
        if not found_user:
            raise UserNotFoundError
        if not user_service.find_another_user_by_userid(new_userid, id, db):
            raise UserAlreadyExistsError
        found_user.userid = new_userid
        db.commit()

    def edit_username(new_username: str, id: str, db):
        if new_username == "" or new_username == None:
            raise InvalidUserDataError
        found_user = user_service.find_user_by_id(id, db)
        if not found_user:
            raise UserNotFoundError
        found_user.username = new_username
        db.commit()

    def edit_email(new_email: str, id: str, db):
        if new_email == "" or new_email == None:
            raise InvalidUserDataError
        found_user = user_service.find_user_by_id(id, db)
        if not found_user:
            raise UserNotFoundError
        if not user_service.find_another_user_by_email(new_email, id, db):
            raise UserAlreadyExistsError
        found_user.email = new_email
        db.commit()

    def edit_password(new_password: str, id: str, db):
        if new_password == "" or new_password == None:
            raise InvalidUserDataError
        found_user = user_service.find_user_by_id(id, db)
        if not found_user:
            raise UserNotFoundError
        found_user.password = new_password
        db.commit()

    def delete_user_by_id(id: str, db):
        result = db.query(user).filter(user.id == id).delete()
        db.commit()
        return result

    def delete_user_by_userid(userid: str, db):
        result = db.query(user).filter(user.userid == userid).delete()
        db.commit()
        return result
