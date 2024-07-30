from sqlalchemy import extract
from Database.models import *
from Data.schedule import *
from Data.calendar import *
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

    def get_month_schedule(year: str, month: str, userid: str):
        try:
            year_int = int(year)
            month_int = int(month)
        except Exception as e:
            raise e

        return db.query(schedule).filter(
            extract('year', schedule.date) == year_int,
            extract('month', schedule.date) == month_int,
            schedule.userid == userid
        ).all()
    
    def to_calendar_goal_db(goal_data: calendar_goal_register, userid: str):
        return goal(
            year=goal_data.year,
            month=goal_data.month,
            month_goal=goal_data.month_goal,
            week_goal=goal_data.week_goal,
            userid=userid
        )
    
    def to_calendar_goal_data(goal_entity: calendar_goal):
        return calendar_goal(
            year=goal_entity.year,
            month=goal_entity.month,
            month_goal=goal_entity.month_goal,
            week_goal=goal_entity.week_goal,
            userid=goal_entity.userid
        )
    
    def find_goal(year: int, month: int, userid: str):
        return db.query(goal).filter(
            goal.year == year,
            goal.month == month,
            goal.userid == userid
        ).first()
    
    def register_goal(goal_data: calendar_goal_register, userid: str):
        try:
            if (goal_entity := calendar_service.find_goal(goal_data.year, goal_data.month, userid)) != None:
                goal_entity.month_goal = goal_data.month_goal
                goal_entity.week_goal = goal_data.week_goal
            else:
                goal_entity = calendar_service.to_calendar_goal_db(goal_data, userid)
                db.add(goal_entity)
        except Exception as e:
            raise e
    
    def delete_goal(year: int, month: int, userid: str):
        try:
            db.query(goal).filter(
                goal.year == year,
                goal.month == month,
                goal.userid == userid
            ).delete()
        except Exception as e:
            raise e