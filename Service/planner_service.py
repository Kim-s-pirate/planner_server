from datetime import date
import json

from sqlalchemy import text
from Data.planner import *
from Data.time_table import *
from Data.to_do import *
from Database.models import *
from Database.database import SessionLocal, db
from Service.book_service import *
from Service.subject_service import *

class BookSubjectMismatchError(Exception):
    def __init__(self, message="The subject of the book and the subject of the to-do do not match."):
        self.message = message
        super().__init__(self.message)

class TimeTableOverlapError(Exception):
    def __init__(self, message="The time table is overlapping."):
        self.message = message
        super().__init__(self.message)

class planner_service:
    def to_to_do_db(to_do_data: to_do_register, userid: str, db):
        subject = subject_service.find_subject_by_name(to_do_data.subject, userid, db).subject
        return to_do(
            date=to_do_data.date,
            userid=userid,
            title=to_do_data.title,
            status=to_do_data.status,
            book_title=to_do_data.book_title,
            subject=subject
        )
    
    def to_to_do_data(to_do: to_do):
        return to_do_data(
            date=to_do.date,
            userid=to_do.userid,
            title=to_do.title,
            status=to_do.status,
            book_title=to_do.book_title,
            subject=to_do.subject
        )
    
    def to_time_table_db(time_table_data: time_table_register, userid: str, db):
        subject = subject_service.find_subject_by_name(time_table_data.subject, userid, db).subject
        time = [str(time) for time in list(set(time_table_data.time))]
        return time_table(
            date=time_table_data.date,
            userid=userid,
            time=time,
            subject=subject
        )
    
    def to_time_table_data(time_table: time_table):
        return time_table_data(
            date=time_table.date,
            userid=time_table.userid,
            time=time_table.time,
            subject=time_table.subject
        )

    def find_to_do_by_data(to_do_data: to_do_register, userid: str, db):
        return db.query(to_do).filter(to_do.date == to_do_data.date, to_do.userid == userid, to_do.title == to_do_data.title, to_do.book_title == to_do_data.book_title).first()
    
    def find_time_table_by_data(time_table_data: time_table_register, userid: str, db):
        return db.query(time_table).filter(time_table.date == time_table_data.date, time_table.userid == userid, time_table.subject == time_table_data.subject).first()

    def register_planner(userid: str, planner_data: planner_register, db):
        date = planner_data.date

        to_do_list = planner_data.to_do_list
        to_do_entity_list = planner_service.find_to_do_by_date(date, userid, db)
        to_do_entity_list = [planner_service.to_to_do_data(to_do_entity) for to_do_entity in to_do_entity_list]
        exist_to_do = set(to_do_entity_list)
        to_do_data_set = set(to_do_list)
        to_delete_to_do = exist_to_do - to_do_data_set
        to_add_to_do = to_do_data_set - exist_to_do
        for to_do_data in to_delete_to_do:
            data = planner_service.find_to_do_by_data(to_do_data, userid, db)
            db.delete(data)
        db.commit()
        for to_do_data in to_add_to_do:
            to_do = planner_service.to_to_do_db(to_do_data, userid, db)
            db.add(to_do)
        db.commit()

        time_table_list = planner_data.time_table_list
        time_table_entity_list = planner_service.find_time_table_by_date(date, userid, db)
        time_table_entity_list = [planner_service.to_time_table_data(time_table_entity) for time_table_entity in time_table_entity_list]
        exist_time_table = set(time_table_entity_list)
        time_table_data_set = set(time_table_list)
        to_delete_time_table = exist_time_table - time_table_data_set
        to_add_time_table = time_table_data_set - exist_time_table
        for time_table_data in to_delete_time_table:
            data = planner_service.find_time_table_by_data(time_table_data, userid, db)
            db.delete(data)
        db.commit()
        for time_table_data in to_add_time_table:
            time_table = planner_service.to_time_table_db(time_table_data, userid, db)
            db.add(time_table)
        db.commit()

        planner_entity = planner_service.find_planner_by_date(date, userid, db)
        if planner_entity == None:
            planner_entity = planner(
                date=date,
                userid=userid,
            )
            db.add(planner_entity)
        db.commit()


        

    def find_planner_by_date(date: date, userid: str, db):
        return db.query(planner).filter(planner.date == date, planner.userid == userid).first()

    def delete_planner_by_date(date: date, userid: str, db):
        db.query(planner).filter(planner.date == date, planner.userid == userid).delete()
        db.query(time_table).filter(time_table.date == date, time_table.userid == userid).delete()
        db.query(to_do).filter(to_do.date == date, to_do.userid == userid).delete()
        

    def find_to_do_by_date(date: date, userid: str, db):
        return db.query(to_do).filter(to_do.date == date, to_do.userid == userid).all()
    
    def delete_to_do_by_date(date: date, userid: str, db):
        db.query(to_do).filter(to_do.date == date, to_do.userid == userid).delete()
    
    def find_time_table_by_date(date: date, userid: str, db):
        return db.query(time_table).filter(time_table.date == date, time_table.userid == userid).all()
    
    def delete_time_table_by_date(date: date, userid: str, db):
        db.query(time_table).filter(time_table.date == date, time_table.userid == userid).delete()

    def register_planner_study_time(date: date, userid: str, db):
        time_table_list = planner_service.find_time_table_by_date(date, userid, db)
        study_time = 0
        for time_table_data in time_table_list:
            time_list = time_table_data.time
            study_time += len(time_list)*10
        planner_entity = planner_service.find_planner_by_date(date, userid, db)
        planner_entity.study_time = study_time

    def verify_planner(planner_data: planner_register, userid: str, db):
        for to_do in planner_data.to_do_list:
            if to_do.subject != book_service.find_subject_by_book_title(to_do.book_title, userid, db):
                raise BookSubjectMismatchError
        time_set_list = [set(time_table.time) for time_table in planner_data.time_table_list]
        total = sum(len(s) for s in time_set_list)
        union_total = len(set.union(*time_set_list))
        if total != union_total:
            raise TimeTableOverlapError
        return True