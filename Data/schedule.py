from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class schedule_detail(BaseModel):
    title: str
    detail: str

class day_schedule_register(BaseModel):
    schedule: Optional[List[schedule_detail]]
    date: date

class day_schedule(BaseModel):
    schedule: Optional[List[schedule_detail]]
    userid: str
    date: date

