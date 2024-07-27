from Data.subject import *
from Database.models import *
from Database.database import db

class SubjectNotFoundError(Exception):
    def __init__(self, message="Subject not found."):
        self.message = message
        super().__init__(self.message)

class subject_service:
    def to_subject_db(subject_register: subject_register, userid: str):
        return subject(
            userid=userid,
            subject = subject_register.subject,
        )
    
    def to_subject_data(subject_entity: subject):
        return subject_data(
            id=subject_entity.id,
            userid=subject_entity.userid,
            subject=subject_entity.subject,
        )

    def find_subject_by_name(name: str, userid: str):
        return db.query(subject).filter(subject.subject == name, subject.userid == userid).first()

    def create_subject(subject: subject):
        db.add(subject)

    def delete_subject(name: str):
        db.query(subject).filter(subject.subject == name).delete()
        db.commit()

    def edit_subject_name(name: str, new_name: str, userid: str):
        try:
            found_subject = subject_service.find_subject_by_name(name, userid)
            if found_subject == None:
                raise SubjectNotFoundError
            found_subject.subject = new_name
        except Exception as e:
            raise e
        
    def find_subject_by_userid(userid: str):
        return db.query(subject).filter(subject.userid == userid).all()
