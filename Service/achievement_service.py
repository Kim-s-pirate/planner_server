from datetime import timedelta
from Database.models import result, book
from Data.achievement import *
from Database.database import db
from Service.book_service import *
from Service.error import *
import json


class achievement_service:

    # 해당하는 책의 총 성취도를 반환
    def get_progress_by_book_id(book_id: str, db):
        results = db.query(result).filter(result.book_id == book_id).all()
        unique_pages = set()
        for res in results:
            unique_pages.update(res.page)
        found_book = book_service.find_book_by_id(book_id, db)
        if not found_book:
            raise BookNotFoundError
        total_page = found_book.end_page - found_book.start_page + 1
        progress = len(unique_pages) * 100 / total_page
        return round(progress, 3)

    # 해당하는 기간 중 특정 책에 대한 성취도 반환
    def get_book_progress_by_period(start_date: date, end_date: date, book_id: str, db):
        results = db.query(result).filter(result.date >= start_date, result.date <= end_date,
                                          result.book_id == book_id).all()
        unique_pages = set()
        for res in results:
            unique_pages.update(res.page)
        found_book = book_service.find_book_by_id(book_id, db)
        if not found_book:
            raise BookNotFoundError
        total_page = found_book.end_page - found_book.start_page + 1
        progress = len(unique_pages) * 100 / total_page
        return round(progress, 3)

    # 해당하는 기간 중 각 책에 대한 성취도 반환
    def get_progress_by_period(start_date: date, end_date: date, user_id: str, db):
        results = db.query(result).filter(result.date >= start_date, result.date <= end_date,
                                          result.user_id == user_id).all()
        progress_by_book = {}
        for res in results:
            if res.book_id not in progress_by_book:
                progress_by_book[res.book_id] = set()
            progress_by_book[res.book_id].update(res.page)
        book_progress = {}
        for book_id, pages in progress_by_book.items():
            found_book = book_service.find_book_by_id(book_id, db)
            if found_book:
                total_page = found_book.end_page - found_book.start_page + 1
                progress = len(pages) * 100 / total_page
                book_progress[book_id] = round(progress, 3)
        return book_progress

    # 날짜 하나와 책 id 받아서 그 날짜 이전까지의 전체 진도율 보여주는 코드.
    def get_book_progress_before_date(last_date: date, book_id: str, db):
        results = db.query(result).filter(result.date <= last_date, result.book_id == book_id).all()
        unique_pages = set()
        for res in results:
            unique_pages.update(res.page)
        found_book = book_service.find_book_by_id(book_id, db)
        if not found_book:
            raise BookNotFoundError
        total_page = found_book.end_page - found_book.start_page + 1
        progress = len(unique_pages) * 100 / total_page
        return round(progress, 3)

    # 날짜 하나 받아서 그 날짜 이전까지의 전체 진도율 보여주는 코드.
    def get_progress_before_date(last_date: date, user_id: str, db):
        results = db.query(result).filter(result.date <= last_date, result.user_id == user_id).all()
        progress_by_book = {}
        for res in results:
            if res.book_id not in progress_by_book:
                progress_by_book[res.book_id] = set()
            progress_by_book[res.book_id].update(res.page)
        book_progress = {}
        for book_id, pages in progress_by_book.items():
            found_book = book_service.find_book_by_id(book_id, db)
            if found_book:
                total_page = found_book.end_page - found_book.start_page + 1
                progress = len(pages) * 100 / total_page
                book_progress[book_id] = round(progress, 3)
        return book_progress

    def get_all_progress(start_date: date, end_date: date, user_id: str, db):
        results_between = db.query(result).filter(
            result.date >= start_date,
            result.date <= end_date,
            result.user_id == user_id
        ).all()

        results_before = db.query(result).filter(
            result.date < start_date,
            result.user_id == user_id
        ).all()

        progress_by_book_between = {}
        progress_by_book_before = {}

        for res in results_between:
            if res.book_id not in progress_by_book_between:
                progress_by_book_between[res.book_id] = set()
            progress_by_book_between[res.book_id].update(res.page)

        for res in results_before:
            if res.book_id not in progress_by_book_before:
                progress_by_book_before[res.book_id] = set()
            progress_by_book_before[res.book_id].update(res.page)

        book_progress_between = {}
        book_progress_before = {}
        all_books = db.query(book).all()

        for book_ in all_books:
            book_id = book_.id
            total_page = book_.end_page - book_.start_page + 1

            if book_id in progress_by_book_between:
                pages_between = progress_by_book_between[book_id]
                progress_between = len(pages_between) * 100 / total_page
                book_progress_between[book_id] = round(progress_between, 3)
            else:
                book_progress_between[book_id] = 0.0

            if book_id in progress_by_book_before:
                pages_before = progress_by_book_before[book_id]
                progress_before = len(pages_before) * 100 / total_page
                book_progress_before[book_id] = round(progress_before, 3)
            else:
                book_progress_before[book_id] = 0.0

        return {
            "progress_before": book_progress_before,
            "progress_between": book_progress_between
        }