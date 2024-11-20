from Data.oauth import naver_data, oauth_register
from Database.models import user
from Data.user import *
from Database.database import db
from Service.error import *

class user_service:
    USER_SOUND_MAX = 10
    USER_SOUND_MIN = 0
    
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
            email=user_entity.email,
            sound_setting=user_entity.sound_setting
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
            db.refresh(user)
            return user
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
        if user_service.find_another_user_by_userid(new_userid, id, db):
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
        if user_service.find_another_user_by_email(new_email, id, db):
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

    def register_form_validation(user_register: user_register):
        # email
        if user_register.email == "":
            raise EmptyEmailError
        if " " in user_register.email:
            raise EmailContainsSpacesError
        # userid
        if user_register.userid == "":
            raise EmptyUseridError
        if " " in user_register.userid:
            raise UseridContainsSpacesError
        if len(user_register.userid) < 3 or len(user_register.userid) > 20:
            raise InappositeUseridLengthError
        # username
        if user_register.username == "":
            raise EmptyUsernameError
        # password
        if user_register.password == "":
            raise EmptyPasswordError
        if " " in user_register.password:
            raise PasswordContainsSpacesError
        if len(user_register.password) < 3 or len(user_register.password) > 20:
            raise InappositePasswordLengthError
        
    def oauth_register_form_validation(oauth_register: oauth_register):
        # userid
        if oauth_register.userid == "":
            raise EmptyUseridError
        if " " in oauth_register.userid:
            raise UseridContainsSpacesError
        if len(oauth_register.userid) < 3 or len(oauth_register.userid) > 20:
            raise InappositeUseridLengthError
        # username
        if oauth_register.username == "":
            raise EmptyUsernameError
        
    def register_oauth_naver_user(naver_register: naver_data, oauth_register: oauth_register):
        user_service.oauth_register_form_validation(oauth_register)
        new_user = user(
            userid=oauth_register.userid,
            username=oauth_register.username,
            email=oauth_register.email,
            password="nothing",
            oauth=True
        )
        user_service.create_user(new_user, db)
        return new_user
    
    def update_user_sound_setting(user_id: str, sound_setting: int, db):
        found_user = user_service.find_user_by_id(user_id, db)
        if sound_setting < user_service.USER_SOUND_MIN or sound_setting > user_service.USER_SOUND_MAX:
            raise InvalidSoundSettingError
        if not found_user:
            raise UserNotFoundError
        found_user.sound_setting = sound_setting
        return True