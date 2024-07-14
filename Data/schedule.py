from pydantic import BaseModel
from datetime import date
from typing import Optional

class day_schedule_register(BaseModel):
    schedule: Optional[str]
    date: date

class day_schedule(BaseModel):
    schedule: str
    userid: str
    date: date