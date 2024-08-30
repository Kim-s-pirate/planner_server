from Data.subject import *
from Database.models import *
from Database.database import db
from Service.error import *

# id

COLOR_SET = {'#FF0000', '#FF6A9E', '#FBB8CA',
             '#9E1A1A', '#BC1FFF', '#DA84FF',
             '#8113AF', '#0307FF', '#76A6FF',
             '#D2E2FF', '#002260', '#057917',
             '#13AF2B', '#77EB39', '#1A5022',
             '#FFE209', '#FFF8A7', '#A08E04',
             '#F67F00', '#EFAE67', '#BD611A',
             '#000000', '#858585', '#FFFFFF'}

class subject_service:
    def validate_subject_data(subject_register: subject_register):
        if subject_register.title == "" or subject_register.title is None:
            raise EmptyTitleError

    def to_subject_db(subject_register: subject_register, user_id: str):
        subject_service.validate_subject_data(subject_register)
        try:
            return subject(
                user_id=user_id,
                title=subject_register.title
            )
        except Exception as e:
            raise e

    def to_subject_data(subject_entity: subject):
        return subject_data(
            id=subject_entity.id,
            user_id=subject_entity.user_id,
            title=subject_entity.title,
            color=subject_entity.color
        )

    def create_subject(subject: subject, db):
        try:
            if subject_service.is_title_exists(subject.title, subject.user_id, db):
                raise SubjectAlreadyExistsError
            db.add(subject)
            db.commit()
        except Exception as e:
            raise e

    def find_subject_by_id(id: str, db):
        return db.query(subject).filter(subject.id == id).first()

    def find_subject_by_title(title: str, user_id: str, db):
        return db.query(subject).filter(subject.title == title, subject.user_id == user_id).first()

    def find_another_subject_by_title(title: str, id: str, user_id: str, db):
        return db.query(subject).filter(subject.title == title, subject.user_id == user_id, subject.id != id).first()

    def find_subject_by_user_id(user_id: str, db):
        return db.query(subject).filter(subject.user_id == user_id).all()

    def find_subject_by_color(color: str, user_id: str, db):
        return db.query(subject).filter(subject.color == color, subject.user_id == user_id).first()

    def find_another_subject_by_color(color: str, id: str, user_id: str, db):
        return db.query(subject).filter(subject.color == color, subject.user_id == user_id, subject.id != id).first()

    def is_title_exists(title: str, user_id: str, db):
        return db.query(subject).filter(subject.title == title, subject.user_id == user_id).first() is not None

    def remain_color(user_id: str, db):
        used_color = set([subject.color for subject in subject_service.find_subject_by_user_id(user_id, db)])
        return list(COLOR_SET - used_color)

    def random_color(user_id: str, db):
        remain_color = subject_service.remain_color(user_id, db)
        if not remain_color:
            raise ColorExhaustedError
        return random.choice(remain_color)

    def edit_title(new_title: str, id: str, user_id: str, db):
        if new_title == "" or new_title is None:
            raise EmptyTitleError
        if subject_service.find_another_subject_by_title(new_title, id, user_id, db):
            raise SubjectAlreadyExistsError
        found_subject = subject_service.find_subject_by_id(id, db)
        if not found_subject:
            raise SubjectNotFoundError
        found_subject.title = new_title
        db.commit()

    def edit_color(new_color: str, id: str, user_id: str, db):
        if not new_color in COLOR_SET:
            raise InvalidSubjectDataError
        found_subject = subject_service.find_another_subject_by_color(new_color, id, user_id, db)
        target_subject = subject_service.find_subject_by_id(id, db)
        if not target_subject:
            raise SubjectNotFoundError
        if found_subject is not None:
            found_subject.color = target_subject.color
        target_subject.color = new_color
        db.commit()

    def delete_subject_by_id(id: str, db):
        result = db.query(subject).filter(subject.id == id).delete()
        db.commit()
        return result

    def delete_subject_by_title(title: str, user_id: str, db):
        result = db.query(subject).filter(subject.title == title, subject.user_id == user_id).delete()
        db.commit()
        return result
    
    def find_subject_id_list(user_id: str, db):
        subject_list = db.query(subject).filter(subject.user_id == user_id).all()
        return [subject.id for subject in subject_list]

    # def edit_subject(subject_data: subject_edit, id: str, user_id: str, db):
    #     try:
    #         # 컬러셋 내에서 온 값인지 확인
    #         subject_service.check_title_exists(subject_data.title, user_id, db)
    #         existing_subject = subject_service.find_subject_by_color(subject_data.color, user_id, db)
    #         #######################
    #         if existing_subject is not None:
    #             original_color = subject_service.find_subject_by_id(id, db).color
    #             subject_service.edit_subject_color(original_color, existing_subject.id, db)
    #         subject_service.edit_subject_title(subject_data.title, id, db)
    #         subject_service.edit_subject_color(subject_data.color, id, db)
    #     except SubjectAlreadyExistsError:
    #         raise
    #     except SubjectNotFoundError:
    #         raise
    #     except Exception as e:
    #         raise SubjectUpdateError from e

    # def edit_subject_title(new_title: str, id: str, db):
    #     try:
    #         found_subject = subject_service.find_subject_by_id(id, db)
    #         found_subject.title = new_title
    #         db.commit()
    #     except SubjectNotFoundError:
    #         raise
    #     except Exception as e:
    #         db.rollback()
    #         raise SubjectUpdateError from e