from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from Data.task import task

class day_schedule_register(BaseModel):
    task_list: Optional[List['task']] = []
    date: date

class day_schedule(BaseModel):
    task_list: List['task'] = []
    userid: str
    date: date