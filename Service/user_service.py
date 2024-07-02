from Database.models import user
from Data.user import user_register
from Database.database import db

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
    
    def find_user_by_email(email: str):
        return db.query(user).filter(user.email == email).first()
    
    def find_user_by_userid(userid: str):
        return db.query(user).filter(user.userid == userid).first()
    
    def create_user(user: user):
            db.add(user)