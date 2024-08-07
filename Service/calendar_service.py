from sqlalchemy import extract
from Database.models import *
from Data.schedule import *
from Data.calendar import *
from Data.task import task
from Database.database import db
from datetime import date, datetime
from Service.date_service import date_service
import json


class calendar_service:
    @staticmethod
    def to_schedule_db(schedule_data: day_schedule_register, user_id: str) -> schedule:
        try:
            task_list_json = json.dumps([t.to_dict() for t in schedule_data.task_list])

            return schedule(
                user_id=user_id,
                date=schedule_data.date,
                task_list=task_list_json
            )
        except Exception as e:
            raise e

    @staticmethod
    def to_schedule_data(schedule_entity: schedule):
        task_list = [task.from_dict(t) for t in json.loads(schedule_entity.task_list)]

        return day_schedule(
            user_id=schedule_entity.user_id,
            date=schedule_entity.date,
            task_list=task_list
        )

    @staticmethod
    def schedule_to_dict(schedule_data: day_schedule) -> dict:
        return {
            "user_id": schedule_data.user_id,
            "date": schedule_data.date.isoformat(),
            "task_list": [task.to_dict(t) for t in schedule_data.task_list]
        }

    @staticmethod
    def task_register_to_dict(task_register: task) -> dict:
        return task_register.to_dict()

    @staticmethod
    def find_schedule_by_date(date: date, user_id: str, db) -> schedule:
        return db.query(schedule).filter(schedule.date == date, schedule.user_id == user_id).first()

    @staticmethod
    def delete_schedule(date: date, user_id: str, db):
        existing_schedule = db.query(schedule).filter(schedule.date == date, schedule.user_id == user_id).first()
        if existing_schedule:
            db.delete(existing_schedule)

    @staticmethod
    def register_schedule(schedule_data: day_schedule, db):
        try:
            existing_schedule = calendar_service.find_schedule_by_date(schedule_data.date, schedule_data.user_id, db)
            if existing_schedule:
                db.delete(existing_schedule)
                db.commit()

            if isinstance(schedule_data.task_list, str):
                task_list = [task.from_dict(t) for t in json.loads(schedule_data.task_list)]
            else:
                task_list = schedule_data.task_list

            new_schedule = calendar_service.to_schedule_db(
                day_schedule_register(
                    task_list=task_list,
                    date=schedule_data.date
                ), schedule_data.user_id
            )
            db.add(new_schedule)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_month_schedule(year: str, month: str, user_id: str, db) -> list:
        results = db.query(schedule).filter(
            extract('year', schedule.date) == year,
            extract('month', schedule.date) == month,
            schedule.user_id == user_id
        ).all()

        formatted_results = []
        for result in results:
            formatted_result = schedule(
                date=date_service.get_date(result.date),
                user_id=result.user_id,
                task_list=result.task_list,
            )
            formatted_results.append(formatted_result)

        return formatted_results

    @staticmethod
    def to_calendar_goal_db(goal_data: calendar_goal_register, user_id: str) -> goal:
        return goal(
            year=goal_data.year,
            month=goal_data.month,
            month_goal=goal_data.month_goal,
            week_goal=goal_data.week_goal,
            user_id=user_id
        )

    @staticmethod
    def to_calendar_goal_data(goal_entity: goal) -> calendar_goal:
        return calendar_goal(
            year=goal_entity.year,
            month=goal_entity.month,
            month_goal=goal_entity.month_goal,
            week_goal=goal_entity.week_goal,
            user_id=goal_entity.user_id
        )

    @staticmethod
    def find_goal(year: int, month: int, user_id: str, db) -> goal:
        return db.query(goal).filter(
            goal.year == year,
            goal.month == month,
            goal.user_id == user_id
        ).first()

    @staticmethod
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

    @staticmethod
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
