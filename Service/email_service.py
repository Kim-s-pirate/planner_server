from datetime import timedelta
from sqlalchemy import extract
from Database.models import *
from Database.database import db

class email_service:
    def to_verification_db(email: str, code: str):
        return verification(
            email=email,
            code=code
        )
    
    def find_verification_by_email(email: str, db):
        return db.query(verification).filter(verification.email == email).first()
    
    def register_verification(email: str, code: str, db):
        found = email_service.find_verification_by_email(email, db)
        if found is not None:
            found.code = code
            return True
        db.add(email_service.to_verification_db(email, code))
        return True
    
    # def delete_expired_verification(email: str):
    #     now = datetime.now()
    #     db.query(verification).filter(verification.created_at < now - timedelta(hours=3)).delete()
    #     db.commit()

    def delete_expired_verification(db):
        now = datetime.now()
        db.query(verification).filter(verification.time < now - timedelta(minutes=1)).delete()
        db.commit()