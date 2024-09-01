from sqlalchemy import extract
from Data.d_day import d_day_data, d_day_register
from Database.models import *
from Data.task import task
from Database.database import db
from datetime import date, datetime
from Service.error import *
import json

class d_day_service:
    def to_d_day_db(d_day_data: d_day_register, user_id: str):
        return d_day(
            user_id=user_id,
            title=d_day_data.title,
            date=d_day_data.date
        )
    
    def to_d_day_data(d_day_entity: d_day):
        return d_day_data(
            id=d_day_entity.id,
            user_id=d_day_entity.user_id,
            title=d_day_entity.title,
            date=d_day_entity.date
        )
    
    def create_d_day(d_day: d_day_register, db):
        try:
            if d_day.title in [d_day_temp.title for d_day_temp in d_day_service.find_d_day_by_date(d_day.date, d_day.user_id, db)]:
                raise DDayAlreadyExistsError
            d_day = d_day_service.to_d_day_db(d_day, db)
            db.add(d_day)
            db.commit()
        except Exception as e:
            raise e
        
    def delete_d_day_by_id(id: str, db):
        try:
            db.query(d_day).filter(d_day.id == id).delete()
        except Exception as e:
            raise e
        
    def set_d_day_star(id: str, star: bool, db):
        try:
            d_day = db.query(d_day).filter(d_day.id == id).first()
            d_day.star = star
        except Exception as e:
            raise e
    
    def find_d_day_by_id(id: str, db):
        return db.query(d_day).filter(d_day.id == id).first()
    
    def find_d_day_by_user_id(user_id: str, db):
        return db.query(d_day).filter(d_day.user_id == user_id).all()
    
    def find_d_day_by_date(date: date, user_id: str, db):
        return db.query(d_day).filter(d_day.date == date, d_day.user_id == user_id).all()