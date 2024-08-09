from Data.subject import *
from Database.models import *
from Database.database import db

# id

COLOR_SET = {'#21ACA9', '#34CDEF', '#7475BB',
             '#756C86', '#ACB6B3', '#B5E045',
             '#BFA8EE', '#CB7D60', '#E35BE5',
             '#EE5444', '#EF5A68', '#F7969A',
             '#F8CA8F', '#EDED2A', '#FFD749',
             '#809A79', '#C7DBF8', '#FF94E7',
             '#FF9568', '#D7FFAF'}

class SubjectNotFoundError(Exception):
    def __init__(self, message="Subject not found."):
        self.message = message
        super().__init__(self.message)

class SubjectAlreadyExistsError(Exception):
    def __init__(self, message="Subject already exists."):
        self.message = message
        super().__init__(self.message)

class InvalidSubjectDataError(Exception):
    def __init__(self, message="Invalid subject data."):
        self.message = message
        super().__init__(self.message)

class DatabaseCommitError(Exception):
    def __init__(self, message="Database commit error occurred."):
        self.message = message
        super().__init__(self.message)

class SubjectUpdateError(Exception):
    def __init__(self, message="Failed to update subject."):
        self.message = message
        super().__init__(self.message)

class subject_service:
    def to_subject_db(subject_register: subject_register, user_id: str):
        try:
            subject_db = subject()
            subject_db.user_id = user_id,
            subject_db.subject = subject_register.subject
            return subject_db
        except:
            raise InvalidSubjectDataError

    def to_subject_data(subject_entity: subject):
        return subject_data(
            id=subject_entity.id,
            user_id=subject_entity.user_id,
            subject=subject_entity.subject,
            color=subject_entity.color
        )

    def find_subject_by_id(id: str, db):
        return db.query(subject).filter(subject.id == id).first()

    def find_subject_by_name(name: str, user_id: str, db):
        return db.query(subject).filter(subject.subject == name, subject.user_id == user_id).first()

    def create_subject(subject_entity: subject, db):
        if subject_service.find_subject_by_name(subject_entity.subject, subject_entity.user_id, db) != None:
            raise SubjectAlreadyExistsError
        db.add(subject_entity)

    def delete_subject_by_name(name: str, user_id: str, db):
        db.query(subject).filter(subject.subject == name, subject.user_id == user_id).delete()

    def delete_subject_by_id(id: str, db):
        db.query(subject).filter(subject.id == id).delete()

    def edit_subject_name_by_name(name: str, new_name: str, user_id: str, db):
        try:
            found_subject = subject_service.find_subject_by_name(name, user_id, db)
            if found_subject == None:
                raise SubjectNotFoundError
            found_subject.subject = new_name
        except Exception as e:
            raise e

    def edit_subject_name_by_id(id: str, new_name: str, user_id: str, db):
        try:
            found_subject = subject_service.find_subject_by_id(id, db)
            if found_subject == None:
                raise SubjectNotFoundError
            found_subject.subject = new_name
        except Exception as e:
            raise e

    def find_subject_by_user_id(user_id: str, db):
        return db.query(subject).filter(subject.user_id == user_id).all()

    def random_color(user_id: str, db):
        try:
            used_color = set([subject.color for subject in subject_service.find_subject_by_user_id(user_id, db)])
            return random.choice(list(COLOR_SET - used_color))
        except Exception as e:
            raise e

    def remain_color(user_id: str, db):
        try:
            used_color = set([subject.color for subject in subject_service.find_subject_by_user_id(user_id, db)])
            return list(COLOR_SET - used_color)
        except Exception as e:
            raise e

    def find_subject_by_color(color: str, user_id: str, db):
        try:
            return db.query(subject).filter(subject.color == color, subject.user_id == user_id).first()
        except Exception as e:
            raise e

    def exchange_color(user_id: str, subject: str, original_color: str, exchanged_color: str, db):
        try:
            found_subject = subject_service.find_subject_by_color(exchanged_color, user_id, db)
            found_subject.color = original_color
            found_subject = subject_service.find_subject_by_name(subject, user_id, db)
            found_subject.color = exchanged_color
        except Exception as e:
            raise

    def edit_subject_color(name: str, user_id: str, new_color: str, db):
        try:
            found_subject = subject_service.find_subject_by_name(name, user_id, db)
            if found_subject == None:
                raise SubjectNotFoundError
            found_subject.color = new_color
        except Exception as e:
            raise e