from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from Data.task import task

class day_schedule_register(BaseModel):
    date: date
    task_list: Optional[List['task']] = []

class day_schedule(BaseModel):
    date: date
    user_id: str
    task_list: List['task'] = []

class calendar_goal_register(BaseModel):
    year: int
    month: int
    month_goal: Optional[str]
    week_goal: Optional[str]


class calendar_goal(BaseModel):
    year: int
    month: int
    month_goal: str
    week_goal: str
    userid: str