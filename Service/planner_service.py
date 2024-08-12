from datetime import date
import json

from sqlalchemy import text
from Data.planner import *
from Data.result import result_data
from Data.time_table import *
from Data.to_do import *
from Database.models import *
from Database.database import SessionLocal, db
from Service.book_service import *
from Service.error import *
from Service.subject_service import *



class planner_service:
    # def to_planner_db(planner_data: planner_data, db):
    #     return planner(
    #         date=planner_data.date,
    #         user_id=planner_data.user_id,
    #         study_time=planner_data.study_time
    #     )
    
    def to_planner_data(planner: planner):
        return planner_data(
            date=planner.date,
            user_id=planner.user_id,
            study_time=planner.study_time
        )

    def to_to_do_db(to_do_data: to_do_register, user_id: str, db):
        return to_do(
            date=to_do_data.date,
            user_id=user_id,
            title=to_do_data.title,
            status=to_do_data.status,
            book_id=to_do_data.book_id
        )
    
    def to_to_do_data(to_do: to_do):
        return to_do_data(
            date=to_do.date,
            user_id=to_do.user_id,
            title=to_do.title,
            status=to_do.status,
            book_id=to_do.book_id
        )
    
    def to_time_table_db(time_table_data: time_table_register, user_id: str, db):
        #subject_id = subject_service.find_subject_by_id(time_table_data.subject_id, db).id
        time = [str(time) for time in list(set(time_table_data.time))]
        return time_table(
            date=time_table_data.date,
            user_id=user_id,
            time=time,
            subject_id=time_table_data.subject_id
        )
    
    def to_time_table_data(time_table: time_table):
        return time_table_data(
            date=time_table.date,
            user_id=time_table.user_id,
            time=time_table.time,
            subject_id=time_table.subject_id
        )
    
    def to_result_db(result_data: result_register, user_id: str, db):
        return result(
            date=result_data.date,
            user_id=user_id,
            book_id=result_data.book_id,
            page=result_data.page
        )
    
    def to_result_data(result: result):
        return result_data(
            date=result.date,
            user_id=result.user_id,
            book_id=result.book_id,
            page=result.page
        )

    def find_to_do_by_data(to_do_data: to_do_register, user_id: str, db):
        return db.query(to_do).filter(to_do.date == to_do_data.date, to_do.user_id == user_id, to_do.title == to_do_data.title, to_do.book_id == to_do_data.book_id).first()
    
    def find_time_table_by_data(time_table_data: time_table_register, user_id: str, db):
        return db.query(time_table).filter(time_table.date == time_table_data.date, time_table.user_id == user_id, time_table.subject_id == time_table_data.subject_id).first()

    def register_planner(user_id: str, planner_data: planner_register, db):
        #검증할때 시간이 넘어섰는지, 겹치는지 확인, 페이지가 책의 페이지보다 작거나 이상한지 확인
        date = planner_data.date
        to_do_list = planner_data.to_do_list
        to_do_entity_list = planner_service.find_to_do_by_date(date, user_id, db)
        to_do_entity_list = [planner_service.to_to_do_data(to_do_entity) for to_do_entity in to_do_entity_list]
        exist_to_do = set(to_do_entity_list)
        to_do_data_set = set(to_do_list)
        to_delete_to_do = exist_to_do - to_do_data_set
        to_add_to_do = to_do_data_set - exist_to_do
        for to_do_data in to_delete_to_do:
            data = planner_service.find_to_do_by_data(to_do_data, user_id, db)
            db.delete(data)
        db.commit()
        for to_do_data in to_add_to_do:
            to_do = planner_service.to_to_do_db(to_do_data, user_id, db)
            db.add(to_do)
        db.commit()

        time_table_list = planner_data.time_table_list
        time_table_entity_list = planner_service.find_time_table_by_date(date, user_id, db)
        time_table_entity_list = [planner_service.to_time_table_data(time_table_entity) for time_table_entity in time_table_entity_list]
        exist_time_table = set(time_table_entity_list)
        time_table_data_set = set(time_table_list)
        to_delete_time_table = exist_time_table - time_table_data_set
        to_add_time_table = time_table_data_set - exist_time_table
        for time_table_data in to_delete_time_table:
            data = planner_service.find_time_table_by_data(time_table_data, user_id, db)
            db.delete(data)
        db.commit()
        for time_table_data in to_add_time_table:
            time_table = planner_service.to_time_table_db(time_table_data, user_id, db)
            db.add(time_table)
        db.commit()

        result_list = planner_data.result_list
        result_entity_list = planner_service.find_result_by_date(date, user_id, db)
        result_entity_list = [planner_service.to_result_data(result_entity) for result_entity in result_entity_list]
        exist_result = set(result_entity_list)
        result_data_set = set(result_list)
        to_delete_result = exist_result - result_data_set
        to_add_result = result_data_set - exist_result
        for result_data in to_delete_result:
            data = planner_service.find_result_by_data(result_data, user_id, db)
            db.delete(data)
        db.commit()
        for result_data in to_add_result:
            result = planner_service.to_result_db(result_data, user_id, db)
            db.add(result)
        db.commit()

        planner_entity = planner_service.find_planner_by_date(date, user_id, db)
        if planner_entity == None:
            planner_entity = planner(
                date=date,
                user_id=user_id,
            )
            db.add(planner_entity)
        db.commit()


    def find_result_by_data(result_data: result_register, user_id: str, db):
        return db.query(result).filter(result.date == result_data.date, result.user_id == user_id, result.book_id == result_data.book_id).first()


        

    def find_planner_by_date(date: date, user_id: str, db):
        return db.query(planner).filter(planner.date == date, planner.user_id == user_id).first()

    def delete_planner_by_date(date: date, user_id: str, db):
        db.query(planner).filter(planner.date == date, planner.user_id == user_id).delete()
        db.query(time_table).filter(time_table.date == date, time_table.user_id == user_id).delete()
        db.query(to_do).filter(to_do.date == date, to_do.user_id == user_id).delete()
        

    def find_to_do_by_date(date: date, user_id: str, db):
        return db.query(to_do).filter(to_do.date == date, to_do.user_id == user_id).all()
    
    def delete_to_do_by_date(date: date, user_id: str, db):
        db.query(to_do).filter(to_do.date == date, to_do.user_id == user_id).delete()
    
    def find_time_table_by_date(date: date, user_id: str, db):
        return db.query(time_table).filter(time_table.date == date, time_table.user_id == user_id).all()
    
    def delete_time_table_by_date(date: date, user_id: str, db):
        db.query(time_table).filter(time_table.date == date, time_table.user_id == user_id).delete()

    def register_planner_study_time(date: date, user_id: str, db):
        time_table_list = planner_service.find_time_table_by_date(date, user_id, db)
        study_time = 0
        for time_table_data in time_table_list:
            time_list = time_table_data.time
            study_time += len(time_list)*10
        planner_entity = planner_service.find_planner_by_date(date, user_id, db)
        planner_entity.study_time = study_time

    def verify_planner(planner_data: planner_register, user_id, db):
        time_set_list = [set(time_table.time) for time_table in planner_data.time_table_list]
        total = sum(len(s) for s in time_set_list)
        union_total = len(set.union(*time_set_list))
        if total != union_total:
            raise TimeTableOverlapError
        
        book_id_list = book_service.find_book_id_list(user_id, db)
        for to_do in planner_data.to_do_list:
            if to_do.book_id not in book_id_list:
                raise BookNotFoundError
            
        subject_id_list = subject_service.find_subject_id_list(user_id, db)
        for time_table in planner_data.time_table_list:
            if time_table.subject_id not in subject_id_list:
                raise SubjectNotFoundError
            
        for result in planner_data.result_list:
            if result.book_id not in book_id_list:
                raise BookNotFoundError
            book = book_service.find_book_by_id(result.book_id, db)
            max_page = max(result.page)
            min_page = min(result.page)
            if book.end_page < max_page or book.start_page > min_page:
                raise PageRangeError
            
        return planner_data
    
    def get_planner(user_id: str, date: date, db):
        planner_list = db.query(planner).filter(planner.user_id == user_id, planner.date == date).all()
        return planner_list
    
    def find_result_by_date(date: date, user_id: str, db):
        return db.query(result).filter(result.date == date, result.user_id == user_id).all()