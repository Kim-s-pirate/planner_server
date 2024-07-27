from datetime import date
from Data.planner import planner_data, planner_register
from Data.time_table import time_table
from Data.to_do import to_do
from Database.models import *
from Database.database import db
from Service.subject_service import *

class planner_service:
    def to_planner_db(planner_data: planner_register, userid: str):
        return planner(
            userid=userid,
            date=planner_data.date,
            to_do_list=[planner_service.to_do_register_to_dict(to_do) for to_do in planner_data.to_do_list],
            time_table_list=[planner_service.time_table_register_to_dict(time_table) for time_table in planner_data.time_table_list]
        )
    
    def to_planner_data(planner_entity: planner):
        return planner_data(
            id=planner_entity.id,
            date=planner_entity.date,
            userid=planner_entity.userid,
            to_do_list=[to_do.from_dict(i) for i in planner_entity.to_do_list],
            time_table_list=[time_table.from_dict(i) for i in planner_entity.time_table_list]
        )
    
    def planner_to_dict(planner_data: planner_data):
        return {
            "id": planner_data.id,
            "userid": planner_data.userid,
            "date": planner_data.date.isoformat(),
            "to_do_list": [to_do.to_dict(i) for i in planner_data.to_do_list],
            "time_table_list": [time_table.to_dict(i) for i in planner_data.time_table_list]
        }
    
    def to_do_register_to_dict(to_do_register: to_do):
        return {
            "title": to_do_register.title,
            "status": to_do_register.status,
            "book_title": to_do_register.book_title,
            "subject": to_do_register.subject
        }
    
    def time_table_register_to_dict(time_table_register: time_table):
        return {
            "subject": time_table_register.subject,
            "time": [str(t) for t in time_table_register.time],
        }

    def register_planner(planner_data: planner):
        try:
            planner_entity = planner_service.find_planner_by_date(planner_data.date, planner_data.userid)
            if planner_entity is not None:
                planner_entity.to_do_list = planner_data.to_do_list
                planner_entity.time_table_list = planner_data.time_table_list
            else:
                db.add(planner_data)
        except Exception as e:
            raise e
    
    def find_planner_by_date(date: date, userid: str):
        return db.query(planner).filter(planner.date == date, planner.userid == userid).first()
    
    def subject_validator(planner_data: planner_register, userid: str):
        for time_table in planner_data.time_table_list:
            if time_table.subject is not None:
                if subject_service.find_subject_by_name(time_table.subject, userid) is None:
                    raise SubjectNotFoundError
        return True
    
    def delete_planner(date: date, userid: str):
        db.query(planner).filter(planner.date == date, planner.userid == userid).delete()
        db.commit()