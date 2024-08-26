from sqlalchemy import extract
from Database.models import *
from Data.schedule import *
from Data.calendar import *
from Data.task import task
from Database.database import db
from datetime import date, datetime
from Service.date_service import date_service
from Service.error import *
import json

class calendar_service:
    def to_schedule_db(schedule_data: day_schedule_register, user_id: str):
        try:
            task_list_json = json.dumps([t.to_dict() for t in schedule_data.task_list])
            return schedule(
                user_id=user_id,
                date=schedule_data.date,
                task_list=task_list_json
            )
        except:
            raise InvalidScheduleDataError

    def to_schedule_data(schedule_entity: schedule):
        task_list = [task.from_dict(t) for t in json.loads(schedule_entity.task_list)]
        return day_schedule(
            user_id=schedule_entity.user_id,
            date=schedule_entity.date,
            task_list=task_list
        )

    def schedule_to_dict(schedule_data: day_schedule):
        return {
            "user_id": schedule_data.user_id,
            "date": schedule_data.date.isoformat(),
            "task_list": [task.to_dict(t) for t in schedule_data.task_list]
        }

    def create_schedule(schedule: schedule, db):
        try:
            calendar_service.delete_schedule_by_date(schedule.date, schedule.user_id, db)
            db.add(schedule)
            db.commit()
        except Exception as e:
            raise e

    def find_schedule_by_month(year: str, month: str, user_id: str, db):
        found_schedules = db.query(schedule).filter(
            extract('year', schedule.date) == year,
            extract('month', schedule.date) == month,
            schedule.user_id == user_id
        ).all()
        if not found_schedules:
            return None
        return [
            schedule(
                date=date_service.get_date(result.date),
                user_id=result.user_id,
                task_list=result.task_list,
            )
            for result in found_schedules
        ]

    def find_schedule_by_date(date: date, user_id: str, db):
        found_schedule = db.query(schedule).filter(schedule.date == date, schedule.user_id == user_id).first()
        if not found_schedule:
            return None
        found_schedule.date = date_service.get_date(found_schedule.date)
        return found_schedule

    def delete_schedule_by_date(date: date, user_id: str, db):
        result = db.query(schedule).filter(schedule.date == date, schedule.user_id == user_id).delete()
        db.commit()
        return result

    def delete_schedule_by_month(year: str, month: str, user_id: str, db):
        result = db.query(schedule).filter(
            extract('year', schedule.date) == year,
            extract('month', schedule.date) == month,
            schedule.user_id == user_id
        ).delete()
        db.commit()
        return result






###############################3








    def to_calendar_goal_db(goal_data: calendar_goal_register, user_id: str) -> goal:
        return goal(
            year=goal_data.year,
            month=goal_data.month,
            month_goal=goal_data.month_goal,
            week_goal=goal_data.week_goal,
            user_id=user_id
        )

    def to_calendar_goal_data(goal_entity: goal) -> calendar_goal:
        return calendar_goal(
            year=goal_entity.year,
            month=goal_entity.month,
            month_goal=goal_entity.month_goal,
            week_goal=goal_entity.week_goal,
            user_id=goal_entity.user_id
        )

    def find_goal(year: int, month: int, user_id: str, db) -> goal:
        return db.query(goal).filter(
            goal.year == year,
            goal.month == month,
            goal.user_id == user_id
        ).first()

    def register_goal(goal_data: calendar_goal_register, user_id: str, db):
        try:
            existing_goal = calendar_service.find_goal(goal_data.year, goal_data.month, user_id, db)
            if existing_goal:
                existing_goal.month_goal = goal_data.month_goal
                existing_goal.week_goal = goal_data.week_goal
            else:
                new_goal = calendar_service.to_calendar_goal_db(goal_data, user_id)
                db.add(new_goal)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    def delete_goal(year: int, month: int, user_id: str, db):
        try:
            db.query(goal).filter(
                goal.year == year,
                goal.month == month,
                goal.user_id == user_id
            ).delete()
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
