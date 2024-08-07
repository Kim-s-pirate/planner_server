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


class BookAlreadyExistsError(Exception):
    def __init__(self):
        self.message = "Book already exists"
        super().__init__(self.message)


class DuplicateBookError(Exception):
    def __init__(self, message="This book already exists."):
        self.message = message
        super().__init__(self.message)


class DuplicateBookTitleError(Exception):
    def __init__(self, message="This book already exists."):
        self.message = message
        super().__init__(self.message)


class BookNotFoundError(Exception):
    def __init__(self, message="Book not found."):
        self.message = message
        super().__init__(self.message)


class PageError(Exception):
    def __init__(self, message="Start page cannot be greater than end page."):
        self.message = message
        super().__init__(self.message)


class book_service:
    def to_book_db(book_register: book_register, user_id: str):
        return book(
            user_id=user_id,
            title=book_register.title,
            start_page=book_register.start_page,
            end_page=book_register.end_page,
            memo=book_register.memo,
            **({"status": book_register.status} if book_register.status is not None else True),
            **({"subject_id": book_register.subject_id} if book_register.subject_id is not None else {})
        )

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

    def duplicate_book(title: str, user_id: str, db):
        if db.query(book).filter(book.title == title, book.user_id == user_id).first() is not None:
            return True
        else:
            return False

    def find_book_by_title(title: str, user_id: str, db):
        return db.query(book).filter(book.title == title, book.user_id == user_id).first()

    def find_book_by_partial_title(partial_title: str, user_id: str, db):
        search_pattern = f"%{partial_title}%"
        return db.query(book).filter(book.title.like(search_pattern), book.user_id == user_id).all()

    def find_book_by_id(id: int, db):
        return db.query(book).filter(book.id == id).first()

    def find_book_by_subject_id(subject_id: str, db):
        return db.query(book).filter(book.subject_id == subject_id).all()


    def find_book_by_initial(initial: str, user_id: str, db):
        return db.query(book).filter(book.initial.like(f"%{initial}%"), book.user_id == user_id).all()

    def find_book_by_status(status: bool, user_id: str, db):
        return db.query(book).filter(book.status == status, book.user_id == user_id).all()

    def create_book(book: book, db):
        found = book_service.find_book_by_title(book.title, book.user_id, db)
        if found is not None:
            return False
        db.add(book)

    def delete_book_by_id(id: int, db):
        db.query(book).filter(book.id == id).delete()

    def delete_book_by_name(title: str, user_id: str, db):
        db.query(book).filter(book.title == title, book.user_id == user_id).delete()

    def edit_book_by_id(book_data: book_edit, user_id: str, id: int, db):
        try:
            book = book_service.find_book_by_id(id, db)
            if book == None:
                raise BookNotFoundError
            if book.title != book_data.title and book_service.duplicate_book(book_data.title, user_id, db):
                raise DuplicateBookTitleError
            if book.subject_id != book_data.subject_id and (found_subject := subject_service.find_subject_by_id(book_data.subject_id, db)) == None:
                raise SubjectNotFoundError
            book.title = book_data.title
            book.subject_id = book_data.subject_id
            book.start_page = book_data.start_page
            book.end_page = book_data.end_page
            book.memo = book_data.memo
            book.status = book_data.status
        except Exception as e:
            raise e

    def edit_book_by_title(book_data: book_edit, user_id: str, title: str, db):
        try:
            book = book_service.find_book_by_title(title, user_id, db)
            if book == None:
                raise BookNotFoundError
            if book_data.title != book.title:
                book_service.edit_book_title(title, book_data.title, user_id, db)
            if book_data.start_page != book.start_page or book_data.end_page != book.end_page:
                book_service.edit_book_page(title, book_data.start_page, book_data.end_page, user_id, db)
            if book_data.memo != book.memo:
                book_service.edit_book_memo(title, book_data.memo, user_id, db)
            if book_data.status != book.status:
                book_service.edit_book_status(title, book_data.status, user_id, db)
            if book_data.subject_id != book.subject_id:
                book_service.edit_book_subject(title, book_data.subject, user_id, db)
        except Exception as e:
            raise e

    def edit_book_subject(title: str, new_subject: str, user_id: str, db):
        try:
            found_subject = subject_service.find_subject_by_name(new_subject, user_id, db)
            if found_subject == None:
                raise SubjectNotFoundError
            book = book_service.find_book_by_title(title, user_id, db)
            if book == None:
                raise BookNotFoundError
            book.subject = new_subject
        except Exception as e:
            raise e

    def edit_book_subject_by_id(id: str, new_subject: str, user_id: str, db):
        try:
            found_subject = subject_service.find_subject_by_name(new_subject, user_id, db)
            if found_subject == None:
                raise SubjectNotFoundError
            book = book_service.find_book_by_id(id, db)
            if book == None:
                raise BookNotFoundError
            book.subject = new_subject
        except Exception as e:
            raise e

    def edit_book_title(title: str, new_title: str, user_id: str, db):
        try:
            if book_service.duplicate_book(new_title, user_id, db):
                raise DuplicateBookTitleError
            book = book_service.find_book_by_title(title, user_id, db)
            book.title = new_title
        except Exception as e:
            raise e

    def edit_book_title_by_id(id: str, new_title: str, user_id: str, db):
        try:
            if book_service.duplicate_book(new_title, user_id, db):
                raise DuplicateBookTitleError
            book = book_service.find_book_by_id(id, db)
            book.title = new_title
        except Exception as e:
            raise e

    # def edit_book_status(title: str, status: bool, userid: str, db):
    #     try:
    #         book = book_service.find_book_by_title(title, userid, db)
    #         if book == None:
    #             raise BookNotFoundError
    #         book.status = status
    #     except Exception as e:
    #         raise e

    # def edit_book_memo(title: str, memo: str, userid: str, db):
    #     try:
    #         book = book_service.find_book_by_title(title, userid, db)
    #         if book == None:
    #             raise BookNotFoundError
    #         book.memo = memo
    #     except Exception as e:
    #         raise e

    # def edit_book_page(title: str, start_page: int, end_page: int, userid: str, db):
    #     try:
    #         book = book_service.find_book_by_title(title, userid, db)
    #         if book == None:
    #             raise BookNotFoundError
    #         if start_page > end_page:
    #             raise PageError
    #         book.start_page = start_page
    #         book.end_page = end_page
    #     except Exception as e:
    #         raise e

    def find_subject_by_book_title(booktitle: str, user_id: str, db):
        return db.query(book).filter(book.title == booktitle, book.user_id == user_id).first().subject

    def find_subject_by_book_id(id: str, db):
        return db.query(book).filter(book.id == id).first().subject

    def find_book_by_subject(subject: str, user_id: str, db):
        return db.query(book).filter(book.subject == subject, book.user_id == user_id).all()