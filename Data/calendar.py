from pydantic import BaseModel
from datetime import date
from typing import Optional

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