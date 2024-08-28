from datetime import datetime
from Database.database import get_db
from Database.models import log
from Data.user import user_userid
from Service.error import *

class log_service:
    def create_log(userid: str, log_detail: str, time: datetime = datetime.now()):
        try:
            db = get_db()
            new_log = log(user_id=userid, log=log_detail, time=time)
            db.add(new_log)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()