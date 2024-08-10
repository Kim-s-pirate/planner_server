from Database.database import db
from Database.models import log
from Data.user import userid
from Service.error import *

class log_service:
    def create_log(userid: userid, log: str, db):
        try:
            db.add(log)
            db.commit()
        except:
            db.rollback()
            return False
        return True