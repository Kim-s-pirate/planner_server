from Database.models import book, subject
from Data.book import *
from Database.database import db
from Service.subject_service import *

INITIAL_LIST = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ",
    "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

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
    def to_book_db(book_register: book_register, userid: str):
        return book(
            userid=userid,
            title=book_register.title,
            start_page=book_register.start_page,
            end_page=book_register.end_page,
            memo=book_register.memo,
            **({"status": book_register.status} if book_register.status is not None else True),
            **({"subject": book_register.subject} if book_register.subject is not None else {})
        )

    def to_book_data(book_entity: book):
        return book_data(
            id = book_entity.id,
            userid=book_entity.userid,
            title=book_entity.title,
            start_page=book_entity.start_page,
            end_page=book_entity.end_page,
            memo=book_entity.memo,
            status=book_entity.status,
            subject=book_entity.subject
        )
    
    def get_initial(char):
        base_code = 0xAC00
        # 유니코드 값
        unicode_value = ord(char)

        if '가' <= char <= '힣':
            # 초성 인덱스 계산
            initial_index = (unicode_value - base_code) // (21 * 28)
            # 초성 반환
            return INITIAL_LIST[initial_index]
        elif 'a' <= char <= 'z' or 'A' <= char <= "Z":
            return char

    def convert_text_to_initial(text):
        return ''.join(book_service.get_initial(char) or '' for char in text)
    
    def duplicate_book(title: str, userid: str):
        if db.query(book).filter(book.title == title, book.userid == userid).first() is not None:
            return True
        else:
            return False

    def find_book_by_title(title: str, userid: str):
        return db.query(book).filter(book.title == title, book.userid == userid).first()

    def find_book_by_id(id: int):
        return db.query(book).filter(book.id == id).first()
    
    def find_book_by_subject(subject: str, userid: str):
        return db.query(book).filter(book.subject == subject, book.userid == userid).all()

    def find_book_by_initial(initial: str, userid: str):
        return db.query(book).filter(book.initial.like(f"%{initial}%"), book.userid == userid).all()

    def create_book(book: book):
        found = book_service.find_book_by_title(book.title, book.userid)
        if found is not None:
            return False
        db.add(book)

    def delete_book(title: str, userid: str):
        db.query(book).filter(book.title == title, book.userid == userid).delete()
        db.commit()

    def edit_book(book_data: book_edit, userid: str, title: str):
        try:
            book = book_service.find_book_by_title(title, userid)
            if book == None:
                raise BookNotFoundError
            if book_data.title != book.title:
                book_service.edit_book_title(title, book_data.title, userid)
            if book_data.start_page != book.start_page or book_data.end_page != book.end_page:
                book_service.edit_book_page(title, book_data.start_page, book_data.end_page, userid)
            if book_data.memo != book.memo:
                book_service.edit_book_memo(title, book_data.memo, userid)
            if book_data.status != book.status:
                book_service.edit_book_status(title, book_data.status, userid)
            if book_data.subject != book.subject:
                book_service.edit_book_subject(title, book_data.subject, userid)
        except Exception as e:
            raise e
        
    def edit_book_subject(title: str, new_subject: str, userid: str):
        try:
            found_subject = subject_service.find_subject_by_name(new_subject, userid)
            if found_subject == None:
                raise SubjectNotFoundError
            book = book_service.find_book_by_title(title, userid)
            if book == None:
                raise BookNotFoundError
            book.subject = new_subject
        except Exception as e:
            raise e
        
    def edit_book_title(title: str, new_title: str, userid: str):
        try:
            if book_service.duplicate_book(new_title, userid):
                raise DuplicateBookTitleError
            book = book_service.find_book_by_title(title, userid)
            book.title = new_title
        except Exception as e:
            raise e
        
    def edit_book_status(title: str, status: bool, userid: str):
        try:
            book = book_service.find_book_by_title(title, userid)
            if book == None:
                raise BookNotFoundError
            book.status = status
        except Exception as e:
            raise e
    
    def edit_book_memo(title: str, memo: str, userid: str):
        try:
            book = book_service.find_book_by_title(title, userid)
            if book == None:
                raise BookNotFoundError
            book.memo = memo
        except Exception as e:
            raise e
    
    def edit_book_page(title: str, start_page: int, end_page: int, userid: str):
        try:
            book = book_service.find_book_by_title(title, userid)
            if book == None:
                raise BookNotFoundError
            if start_page > end_page:
                raise PageError
            book.start_page = start_page
            book.end_page = end_page
        except Exception as e:
            raise e