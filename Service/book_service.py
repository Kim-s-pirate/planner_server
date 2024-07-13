from Database.models import book
from Data.book import *
from Database.database import db

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
            id=book_entity.id,
            userid=book_entity.userid,
            title=book_entity.title,
            start_page=book_entity.start_page,
            end_page=book_entity.end_page,
            memo=book_entity.memo,
            status=book_entity.status,
            subject=book_entity.subject
        )

    def find_book_by_title(title: str):
        return db.query(book).filter(book.title == title).first()

    def find_book_by_id(id: int):
        return db.query(book).filter(book.id == id).first()

    def create_book(book: book):
        db.add(book)

    def delete_book(id: int):
        db.query(book).filter(book.id == id).delete()
        db.commit()