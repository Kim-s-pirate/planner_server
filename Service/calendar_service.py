from sqlalchemy import extract
from Database.models import *
from Data.schedule import *
from Data.calender import *
from Database.database import db

class calendar_service:
    def to_schedule_db(schedule_data: day_schedule, userid: str):
        return schedule(
            userid=userid,
            date=schedule_data.date,
            schedule=schedule_data.schedule
        )
    
    def to_schedule_data(schedule_entity: schedule):
        return day_schedule(
            userid=schedule_entity.userid,
            date=schedule_entity.date,
            schedule=schedule_entity.schedule
        )
    
    def find_schedule_by_date(date: datetime, userid: str):
        return db.query(schedule).filter(schedule.date == date, schedule.userid == userid).first()
    
    def delete_schedule(date: datetime, userid: str):
        db.query(schedule).filter(schedule.date == date, schedule.userid == userid).delete()
        db.commit()

    def register_schedule(schedule_data: day_schedule, userid: str):
        schedule_entity = calendar_service.find_schedule_by_date(schedule_data.date, userid)
        if schedule_entity == None:
            schedule_entity = calendar_service.to_schedule_db(schedule_data, userid)
            db.add(schedule_entity)
        else:
            db.delete(schedule_entity)
            db.commit()
            new_schudule = calendar_service.to_schedule_db(schedule_data, userid)
            db.add(new_schudule)

    def get_month_schedule(year: int, month: int, userid: str):
        return db.query(schedule).filter(
            extract('year', schedule.date) == year,
            extract('month', schedule.date) == month,
            schedule.userid == userid
        ).all()
    
    def to_goal_db(goal_data: week_goal_register, userid: str):
        return goal(
            userid=userid,
            week=goal_data.week,
            goal=goal_data.goal
        )
    