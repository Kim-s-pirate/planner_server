from datetime import timedelta
import json
from Database.models import result
from Data.achievement import *
from Database.database import db
from Service.book_service import *
from Service.error import *

class achievement_service:

    def find_result_by_date(date: date, user_id: str, db):
        return db.query(result).filter(result.date == date, result.user_id == user_id).all()

    # 해당하는 result값에서 book_id 중복 제거하여 리스트를 얻은 후 아래 get_progress_by_book_id_list를 실행하여 기간 중 책에 대한 진행률 리턴
    def find_result_by_period(period: achievement_request, user_id: str, db):
        return db.query(result).filter(result.date >= period.start_date, result.date <= period.end_date, result.user_id == user_id).all()

    def get_progress_by_book_id(book_id: str, db):
        results = db.query(result).filter(result.book_id == book_id).all()
        unique_pages = set()
        for res in results:
            unique_pages.update(res.page)
        found_book = book_service.find_book_by_id(book_id, db)
        total_page = found_book.end_page - found_book.start_page + 1
        progress = len(unique_pages)*100/total_page
        return round(progress, 3)

    def get_book_progress_by_period(period: achievement_request, book_id: str, db):
        results = db.query(result).filter(result.date >= period.start_date, result.date <= period.end_date, result.book_id == book_id).all()
        unique_pages = set()
        for res in results:
            unique_pages.update(res.page)
        found_book = book_service.find_book_by_id(book_id, db)
        total_page = found_book.end_page - found_book.start_page + 1
        progress = len(unique_pages) * 100 / total_page
        return round(progress, 3)
    
    def get_progress_by_book_id_list(book_id_list: List[str], db):
        progress_list = []
        for book_id in book_id_list:
            progress = achievement_service.get_progress_by_book_id(book_id, db)
            progress_list.append(progress)
        return progress_list
    
    def generate_dates_between(start_date: date, end_date: date):
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        return date_list