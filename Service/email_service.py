from datetime import timedelta
from sqlalchemy import extract
from Database.models import *
from Database.database import db
import re

class email_service:
    def to_verification_db(email: str, code: str):
        return verification(
            email=email,
            code=code
        )
    
    def find_verification_by_email(email: str, db):
        now = datetime.now()
        return db.query(verification).filter(verification.email == email, verification.expire_time > now).first()
    
    def register_verification(email: str, code: str, db):
        found = email_service.find_verification_by_email(email, db)
        if found is not None:
            found.code = code
            db.commit()
            return True
        db.add(email_service.to_verification_db(email, code))
        db.commit()
        return True

    def delete_expired_verification(db):
        now = datetime.now()
        db.query(verification).filter(verification.expire_time < now).delete()
        db.commit()

    def register_state(email: str, state_: str, db):
        found = db.query(state).filter(state.email == email).first()
        if found is not None:
            found.state = state
            db.commit()
            return True
        db.add(state(email=email, state=state_))
        db.commit()
        return True
    
    def find_state(email: str, db):
        return db.query(state).filter(state.email == email).first()
    
    def is_valid_email(email: str) -> bool:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None