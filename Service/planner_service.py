from datetime import date
import json
from Data.planner import *
from Data.time_table import *
from Data.to_do import *
from Database.models import *
from Database.database import db
from Service.subject_service import *

class planner_service:
    def to_to_do_db(to_do_data: to_do_register, userid: str):
        subject = subject_service.find_subject_by_name(to_do_data.subject, userid).subject
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
    
    def to_time_table_db(time_table_data: time_table_register, userid: str):
        subject = subject_service.find_subject_by_name(time_table_data.subject, userid).subject
        time = list(set(time_table_data.time))
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
            subject=time_table.subject.subject
        )
    
    def register_planner(userid: str, planner_data: planner_register):
        date = planner_data.date

        to_do_list = planner_data.to_do_list
        to_do_entity_list = planner_service.find_to_do_by_date(date, userid)
        to_do_entity_list = [planner_service.to_to_do_data(to_do_entity) for to_do_entity in to_do_entity_list]
        exist_to_do = set(to_do_entity_list)
        to_do_data_set = set(to_do_list)
        to_delete_to_do = exist_to_do - to_do_data_set
        to_add_to_do = to_do_data_set - exist_to_do
        for to_do_data in to_delete_to_do:
            db.delete(to_do_data)
        for to_do_data in to_add_to_do:
            to_do = planner_service.to_to_do_db(to_do_data, userid)
            db.add(to_do)

        time_table_list = planner_data.time_table_list
        for time_table_data in time_table_list:
            time_table_data.time = [str(time) for time in time_table_data.time]
        time_table_entity_list = planner_service.find_time_table_by_date(date, userid)
        time_table_entity_list = [planner_service.to_time_table_data(time_table_entity) for time_table_entity in time_table_entity_list]
        exist_time_table = set(time_table_entity_list)
        time_table_data_set = set(time_table_list)
        to_delete_time_table = exist_time_table - time_table_data_set
        to_add_time_table = time_table_data_set - exist_time_table
        for time_table_data in to_delete_time_table:
            db.delete(time_table_data)
        for time_table_data in to_add_time_table:
            time_table = planner_service.to_time_table_db(time_table_data, userid)
            print(type(time_table.subject))
            db.add(time_table)
        planner_entity = planner(
            date=date,
            userid=userid,
        )
        db.add(planner_entity)
        db.commit()
        

        

    def find_planner_by_date(date: date, userid: str):
        return db.query(planner).filter(planner.date == date, planner.userid == userid).first()

    def delete_planner_by_date(date: date, userid: str):
        db.query(planner).filter(planner.date == date, planner.userid == userid).delete()
        db.query(time_table).filter(time_table.date == date, time_table.userid == userid).delete()
        db.query(to_do).filter(to_do.date == date, to_do.userid == userid).delete()
        

    def find_to_do_by_date(date: date, userid: str):
        return db.query(to_do).filter(to_do.date == date, to_do.userid == userid).all()
    
    def delete_to_do_by_date(date: date, userid: str):
        db.query(to_do).filter(to_do.date == date, to_do.userid == userid).delete()
    
    def find_time_table_by_date(date: date, userid: str):
        return db.query(time_table).filter(time_table.date == date, time_table.userid == userid).all()
    
    def delete_time_table_by_date(date: date, userid: str):
        db.query(time_table).filter(time_table.date == date, time_table.userid == userid).delete()

    def register_planner_study_time(date: date, userid: str):
        time_table_list = planner_service.find_time_table_by_date(date, userid)
        study_time = 0
        for time_table_data in time_table_list:
            time_list = time_table_data.time
            study_time += len(time_list)*10
        planner_entity = planner_service.find_planner_by_date(date, userid)
        planner_entity.study_time = study_time

