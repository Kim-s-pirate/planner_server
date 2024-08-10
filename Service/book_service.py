from Database.models import book, subject
from Data.book import *
from Database.database import db
from Service.subject_service import *

# id

# initial setting
INITIAL_LIST = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ",
    "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

class BookNotFoundError(Exception):
    def __init__(self, message="Book not found"):
        self.message = message
        super().__init__(self.message)

class BookAlreadyExistsError(Exception):
    def __init__(self, message="Book already exists"):
        self.message = message
        super().__init__(self.message)

class DuplicateBookTitleError(Exception):
    def __init__(self, message="This book already exists"):
        self.message = message
        super().__init__(self.message)

class InvalidBookDataError(Exception):
    def __init__(self, message="Invalid book data"):
        self.message = message
        super().__init__(self.message)

class DatabaseCommitError(Exception):
    def __init__(self, message="Database commit error occurred"):
        self.message = message
        super().__init__(self.message)

class BookUpdateError(Exception):
    def __init__(self, message="Failed to update book"):
        self.message = message
        super().__init__(self.message)

class PageRangeError(Exception):
    def __init__(self, message="Start page cannot be greater than end page"):
        self.message = message
        super().__init__(self.message)

class NegativePageNumberError(Exception):
    def __init__(self, message="Page number cannot be negative"):
        self.message = message
        super().__init__(self.message)

class book_service:
    def to_book_db(book_register: book_register, user_id: str):
        try:
            return book(
                user_id=user_id,
                title=book_register.title,
                start_page=book_register.start_page,
                end_page=book_register.end_page,
                memo=book_register.memo,
                **({"status": book_register.status} if book_register.status is not None else True),
                **({"subject_id": book_register.subject_id} if book_register.subject_id is not None else {})
            )
        except:
            raise InvalidBookDataError

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

    def create_book(book: book, db):
        try:
            book_service.check_title_exists(book.title, book.user_id, db)
            db.add(book)
            db.commit()
        except BookAlreadyExistsError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e

    def find_book_by_id(id: int, db):
        book_from_id = db.query(book).filter(book.id == id).first()
        if not book_from_id:
            raise BookNotFoundError
        return book_from_id

    def find_book_by_title(title: str, user_id: str, db):
        book_from_title = db.query(book).filter(book.title == title, book.user_id == user_id).first()
        if not book_from_title:
            raise BookNotFoundError
        return book_from_title

    def find_book_by_partial_title(partial_title: str, user_id: str, db):
        search_pattern = f"%{partial_title}%"
        book_from_partial_title = db.query(book).filter(book.title.like(search_pattern), book.user_id == user_id).all()
        if not book_from_partial_title:
            raise BookNotFoundError
        return book_from_partial_title

    def find_book_by_user_id(user_id: str, db):
        book_from_user_id = db.query(book).filter(book.user_id == user_id).all()
        if not book_from_user_id:
            raise BookNotFoundError
        return book_from_user_id

    def find_book_by_subject_id(subject_id: str, db):
        book_from_subject_id = db.query(book).filter(book.subject_id == subject_id).all()
        if not book_from_subject_id:
            raise BookNotFoundError
        return book_from_subject_id

    def find_book_by_subject(title: str, user_id, db):
        try:
            subject_id = subject_service.find_subject_by_title(title, user_id, db).id
            found_book = book_service.find_book_by_subject_id(subject_id, db)
            return found_book
        except SubjectNotFoundError:
            raise
        except BookNotFoundError:
            raise


    def find_book_by_status(status: bool, user_id: str, db):
        book_from_status = db.query(book).filter(book.status == status, book.user_id == user_id).all()
        if not book_from_status:
            raise BookNotFoundError
        return book_from_status

    def find_book_by_initial(initial: str, user_id: str, db):
        book_from_initial = db.query(book).filter(book.initial.like(f"%{initial}%"), book.user_id == user_id).all()
        if not book_from_initial:
            raise BookNotFoundError
        return book_from_initial

    def check_title_exists(title: str, user_id: str, db):
        try:
            book_service.find_book_by_title(title, user_id, db)
            raise BookAlreadyExistsError
        except BookNotFoundError:
            pass
        except BookAlreadyExistsError:
            raise BookAlreadyExistsError(f"Book '{title}' already exists.")
        except Exception as e:
            raise e

    # 각 서비스에서 반복적인 db 쿼리를 실행해서 이런 형식 말고 독립적으로 만드는 것도 좋을듯
    def edit_book(book_data: book_edit, id: str, user_id: str, db):
        try:
            book_service.edit_book_title(book_data.title, id, user_id, db)
            book_service.edit_book_subject_id(book_data.subject_id, id, db)
            book_service.edit_book_page(book_data.start_page, book_data.end_page, id, db)
            book_service.edit_book_memo(book_data.memo, id, db)
            book_service.edit_book_status(book_data.status, id, db)
        except BookAlreadyExistsError:
            raise
        except BookNotFoundError:
            raise
        except SubjectNotFoundError:
            raise
        except NegativePageNumberError:
            raise
        except PageRangeError:
            raise
        except BookUpdateError:
            raise
        except Exception as e:
            raise e

    def edit_book_title(new_title: str, id: str, user_id: str, db):
        try:
            book_service.check_title_exists(new_title, user_id, db)
            found_book = book_service.find_book_by_id(id, db)
            found_book.title = new_title
            db.commit()
        except BookAlreadyExistsError:
            raise
        except BookNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise BookUpdateError from e

    def edit_book_subject_id(new_subject_id: str, id: str, db):
        try:
            subject_service.find_subject_by_id(new_subject_id, db)
            found_book = book_service.find_book_by_id(id, db)
            found_book.subject_id = new_subject_id
            db.commit()
        except SubjectNotFoundError:
            raise
        except BookNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise BookUpdateError from e

    def edit_book_page(new_start_page: int, new_end_page: int, id: str, db):
        try:
            book_service.check_page_validity(new_start_page, new_end_page)
            found_book = book_service.find_book_by_id(id, db)
            found_book.start_page = new_start_page
            found_book.end_page = new_end_page
            db.commit()
        except NegativePageNumberError:
            raise
        except PageRangeError:
            raise
        except BookNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise BookUpdateError from e

    def edit_book_memo(new_memo: str, id: str, db):
        try:
            found_book = book_service.find_book_by_id(id, db)
            found_book.memo = new_memo
            db.commit()
        except BookNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise BookUpdateError from e

    def edit_book_status(new_status: bool, id: str, db):
        try:
            found_book = book_service.find_book_by_id(id, db)
            found_book.status = new_status
            db.commit()
        except BookNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise BookUpdateError from e

    def delete_book_by_id(id: int, db):
        try:
            result = db.query(book).filter(book.id == id).delete()
            if result == False:
                raise BookNotFoundError
            db.commit()
        except BookNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e

    def delete_book_by_title(title: str, user_id: str, db):
        try:
            result = db.query(book).filter(book.title == title, book.user_id == user_id).delete()
            if result == False:
                raise BookNotFoundError
            db.commit()
        except BookNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e

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

    def check_page_validity(start_page: int, end_page: int):
        if start_page < 0 or end_page < 0:
            raise NegativePageNumberError
        if start_page > end_page:
            raise PageRangeError