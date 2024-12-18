from Database.models import book, subject
from Data.book import *
from Database.database import db
from Service.subject_service import *
from Service.error import *



# id

# initial setting
INITIAL_LIST = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ",
    "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]


class book_service:
    def validate_book_data(book_register: book_register):
        if book_register.title == "" or book_register.title is None:
            raise EmptyTitleError
        if book_register.start_page < 0:
            raise NegativePageNumberError
        if book_register.end_page < 0:
            raise NegativePageNumberError
        if book_register.start_page > book_register.end_page:
            raise PageRangeError

    def to_book_db(book_register: book_register, user_id: str):
        try:
            book_service.validate_book_data(book_register)
            return book(
                user_id=user_id,
                title=book_register.title,
                start_page=book_register.start_page,
                end_page=book_register.end_page,
                memo=book_register.memo,
                **({"status": book_register.status} if book_register.status is not None else True),
                **({"subject_id": book_register.subject_id} if book_register.subject_id is not None else {})
            )
        except Exception as e:
            raise e

    def to_book_data(book_entity: book):
        return book_data(
            id=book_entity.id,
            user_id=book_entity.user_id,
            title=book_entity.title,
            start_page=book_entity.start_page,
            end_page=book_entity.end_page,
            memo=book_entity.memo,
            status=book_entity.status,
            subject_id=book_entity.subject_id,
            initial=book_entity.initial
        )

    def register_book(book: book, db):
        try:
            if book_service.is_title_exists(book.title, book.user_id, db):
                raise BookAlreadyExistsError
            if book.subject_id and db.query(subject).filter(subject.id == book.subject_id).first() is None:
                raise SubjectNotFoundError
            if book.start_page < 0:
                raise NegativePageNumberError
            if book.end_page < 0:
                raise NegativePageNumberError
            if book.start_page > book.end_page:
                raise PageRangeError
            if book.start_page > 9999 or book.end_page > 9999:
                raise ExceedPageError
            db.add(book)
            db.commit()
            db.refresh(book)
            return book
        except Exception as e:
            raise e

    def find_book_by_id(id: str, db):
        return db.query(book).filter(book.id == id).first()

    def find_book_by_title(title: str, user_id: str, db):
        return db.query(book).filter(book.title == title, book.user_id == user_id).first()

    def find_book_by_partial_title(partial_title: str, user_id: str, db):
        return db.query(book).filter(book.title.like(f"%{partial_title}%"), book.user_id == user_id).all()

    def find_book_by_user_id(user_id: str, db):
        return db.query(book).filter(book.user_id == user_id).all()

    def find_book_by_subject_id(subject_id: str, db):
        return db.query(book).filter(book.subject_id == subject_id).all()

    def find_book_by_subject(title: str, user_id, db):
        subject = subject_service.find_subject_by_title(title, user_id, db)
        if not subject:
            return []
        return book_service.find_book_by_subject_id(subject.id, db)

    def find_book_id_list(user_id: str, db):
        book_list = db.query(book).filter(book.user_id == user_id).all()
        return [book.id for book in book_list]

    def find_book_by_status(status: bool, user_id: str, db):
        return db.query(book).filter(book.status == status, book.user_id == user_id).all()

    def find_book_by_initial(initial: str, user_id: str, db):
        return db.query(book).filter(book.initial.like(f"%{initial}%"), book.user_id == user_id).all()

    def is_title_exists(title: str, user_id: str, db):
        return db.query(book).filter(book.title == title, book.user_id == user_id).first() is not None

    def edit_title(new_title: str, id: str, user_id: str, db):
        if new_title == "" or new_title is None:
            raise EmptyTitleError
        if book_service.is_title_exists(new_title, user_id, db):
            raise BookAlreadyExistsError
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise BookNotFoundError
        found_book.title = new_title
        db.commit()
        db.refresh(found_book)
        return found_book

    def edit_subject_id(new_subject_id: str, id: str, db):
        if subject_service.find_subject_by_id(new_subject_id, db) is None:
            raise SubjectNotFoundError
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise BookNotFoundError
        found_book.subject_id = new_subject_id
        db.commit()
        db.refresh(found_book)
        return found_book

    def edit_page(new_start_page: int, new_end_page: int, id: str, db):
        if new_start_page < 0:
            raise NegativePageNumberError
        if new_end_page < 0:
            raise NegativePageNumberError
        if new_start_page > new_end_page:
            raise PageRangeError
        if new_start_page > 9999 or new_end_page > 9999:
            raise ExceedPageError
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise BookNotFoundError
        found_book.start_page = new_start_page
        found_book.end_page = new_end_page
        db.commit()
        db.refresh(found_book)
        return found_book

    def edit_memo(new_memo: str, id: str, db):
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise BookNotFoundError
        found_book.memo = new_memo
        db.commit()
        db.refresh(found_book)
        return found_book

    def edit_status(new_status: bool, id: str, db):
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise BookNotFoundError
        found_book.status = new_status
        db.commit()
        db.refresh(found_book)
        return found_book

    def delete_book_by_id(id: str, db):
        result = db.query(book).filter(book.id == id).delete()
        db.commit()
        return result

    def delete_book_by_title(title: str, user_id: str, db):
        result = db.query(book).filter(book.title == title, book.user_id == user_id).delete()
        db.commit()
        return result

    def get_initial(char):
        base_code = 0xAC00
        unicode_value = ord(char)

        if '가' <= char <= '힣':
            initial_index = (unicode_value - base_code) // (21 * 28)
            return INITIAL_LIST[initial_index]
        elif 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            return char
        elif '0' <= char <= '9':
            return char
        elif char == ' ':
            return ''
        else:
            return char

    def convert_text_to_initial(text):
        return ''.join(book_service.get_initial(char) or '' for char in text)