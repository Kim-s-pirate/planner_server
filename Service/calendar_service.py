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
            calendar_service.clean_day_schedule(schedule.date, schedule.user_id, db)
            ########## 직접 테스트로 하나로 확정
            # if isinstance(schedule.task_list, str):
            #     task_list = [task.from_dict(t) for t in json.loads(schedule.task_list)]
            # else:
            #     task_list = schedule.task_list
            #
            # new_schedule = calendar_service.to_schedule_db(
            #     day_schedule_register(
            #         task_list=task_list,
            #         date=schedule_data.date
            #     ), schedule_data.user_id
            # )
            # db.add(new_schedule)
            db.add(schedule)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    def clean_day_schedule(date: date, user_id: str, db):
        try:
            calendar_service.delete_schedule_by_date(date, user_id, db)
        except ScheduleNotFoundError:
            pass
        except Exception as e:
            raise e

    def find_schedule_by_month(year: str, month: str, user_id: str, db):
        try:
            schedule_from_month = db.query(schedule).filter(
                extract('year', schedule.date) == year,
                extract('month', schedule.date) == month,
                schedule.user_id == user_id
            ).all()
            if not schedule_from_month:
                raise ScheduleNotFoundError
            formatted_results = [
                schedule(
                    date=date_service.get_date(result.date),
                    user_id=result.user_id,
                    task_list=result.task_list,
                )
                for result in schedule_from_month
            ]
            return formatted_results
        except ScheduleNotFoundError:
            raise
        except Exception as e:
            raise e

    def find_schedule_by_date(date: date, user_id: str, db):
        schedule_from_date = db.query(schedule).filter(schedule.date == date, schedule.user_id == user_id).first()
        if not schedule_from_date:
            raise ScheduleNotFoundError
        schedule_from_date.date = date_service.get_date(schedule_from_date.date)
        return schedule_from_date

    def delete_schedule_by_date(date: date, user_id: str, db):
        try:
            result = db.query(schedule).filter(schedule.date == date, schedule.user_id == user_id).delete()
            if result == False:
                raise ScheduleNotFoundError
            db.commit()
        except ScheduleNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e

    def delete_schedule_by_month(year: str, month: str, user_id: str, db):
        try:
            result = db.query(schedule).filter(
                extract('year', schedule.date) == year,
                extract('month', schedule.date) == month,
                schedule.user_id == user_id
            ).delete()
            if result == False:
                raise ScheduleNotFoundError
            db.commit()
        except ScheduleNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseCommitError from e


    #####################
















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
