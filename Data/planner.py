from pydantic import BaseModel, validator
from typing import List, Optional
from Data.to_do import to_do
from Data.time_table import time_table
from datetime import date

from Service import subject_service

class planner_register(BaseModel):
    date: date
    to_do_list: Optional[List['to_do']] = []
    time_table_list: Optional[List['time_table']] = []

class planner_data(BaseModel):
    id: int
    date: date
    userid: str
    to_do_list: List['to_do'] = []
    time_table_list: List['time_table'] = []