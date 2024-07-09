from Database.models import book
from Data.book import *
from Database.database import db

class book_service:
    def to_book_db(book_register: book_register, userid: str):
        book_db = book()
        book_db.title = book_register.title
        book_db.userid = userid
        book_db.start_page = book_register.start_page
        book_db.end_page = book_register.end_page
        book_db.memo = book_register.memo
        return book_db

    def to_book_data(book_entity: book):
        book_data = book_data()
        book_data.id = book_entity.id
        book_data.userid = book_entity.userid
        book_data.title = book_entity.title
        book_data.start_page = book_entity.start_page
        book_data.end_page = book_entity.end_page
        book_data.memo = book_entity.memo
        return book_data

    def find_book_by_title(title: str):
        return db.query(book).filter(book.title == title).first()

    def find_book_by_id(id: int):
        return db.query(book).filter(book.id == id).first()

    def create_book(book: book):
        db.add(book)

    def delete_book(id: int):
        db.query(book).filter(book.id == id).delete()
        db.commit()