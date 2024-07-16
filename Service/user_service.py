from Database.models import user
from Data.user import *
from Database.database import db

class UserNotFoundError(Exception):
    def __init__(self, message="User not found."):
        self.message = message
        super().__init__(self.message)

class user_service:
    def to_user_db(user_register: user_register):
        user_db = user()
        user_db.userid = user_register.userid
        user_db.username = user_register.username
        user_db.email = user_register.email
        user_db.password = user_register.password
        return user_db
    
    def to_user_data(user_entity: user):
        user_register = user_register()
        user_register.userid = user_entity.userid
        user_register.username = user_entity.username
        user_register.email = user_entity.email
        user_register.password = user_entity.password
        return user_register
    
    def find_user_by_id(id: int):
        return db.query(user).filter(user.id == id).first()
    
    def find_user_by_email(email: str):
        return db.query(user).filter(user.email == email).first()
    
    def find_user_by_userid(userid: str):
        return db.query(user).filter(user.userid == userid).first()
    
    def create_user(user: user):
        db.add(user)

    def delete_user(userid: str):
        db.query(user).filter(user.userid == userid).delete()
        db.commit()
    
    # 해당 부분은 회의를 통해서 어디까지 수정 가능하게 서비스할지 결정해야함.
    # def edit_user(user_data: user_edit, current_userid: str):
    #     try:
    #         if user_data.userid != current_userid:
    #             user_service.edit_userid(user_data.userid, current_userid)
    #         if user_data.username != current_userid:
    #             user_service.edit_username(user_data.username, current_userid)
    #     except Exception as e:
    #         raise e

    
    def edit_username(new_username: str, userid: str):
        try:
            found_user = user_service.find_user_by_userid(userid)
            if found_user == None:
                raise UserNotFoundError
            found_user.username = new_username
        except Exception as e:
            raise e
    
    def edit_userid(new_userid: str, userid: str):
        try:
            found_user = user_service.find_user_by_userid(userid)
            if found_user == None:
                raise UserNotFoundError
            found_user.userid = new_userid
        except Exception as e:
            raise e
        
    def edit_email(new_email: str, userid: str):
        try:
            found_user = user_service.find_user_by_userid(userid)
            if found_user == None:
                raise UserNotFoundError
            found_user.email = new_email
        except Exception as e:
            raise e
        
    def edit_password(new_password: str, userid: str):
        try:
            found_user = user_service.find_user_by_userid(userid)
            if found_user == None:
                raise UserNotFoundError
            found_user.password = new_password
        except Exception as e:
            raise e