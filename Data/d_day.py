from pydantic import BaseModel
from datetime import date
from typing import Optional

class d_day_register(BaseModel):
    user_id: str
    title: str
    date: date

class d_day_data(BaseModel):
    id: str
    user_id: str
    title: str
    date: date