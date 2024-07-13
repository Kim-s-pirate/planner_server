from Data.subject import *
from Database.models import *
from Database.database import db

class subject_service:
    def to_subject_db(subject_register: subject_register, userid: str):
        return subject(
            userid=userid,
            subject = subject_register.subject,
        )
    
    def to_subject_data(subject_entity: subject):
        return subject_data(
            userid=subject_entity.userid,
            subject=subject_entity.subject,
        )

    def find_subject_by_title(title: str):
        return db.query(book).filter(book.title == title).first()

    def find_subject_by_id(id: int):
        return db.query(book).filter(book.id == id).first()

    def create_subject(subject: book):
        db.add(subject)

    def delete_subject(id: int):
        db.query(book).filter(book.id == id).delete()
        db.commit()