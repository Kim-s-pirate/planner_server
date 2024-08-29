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