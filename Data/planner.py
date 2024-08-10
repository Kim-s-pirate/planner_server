from pydantic import BaseModel, validator
from typing import List, Optional
from Data.result import result_register
from Data.to_do import to_do_register, to_do_data
from Data.time_table import time_table_register, time_table_data
from datetime import date

from Service import subject_service

class planner_register(BaseModel):
    date: date
    to_do_list: Optional[List['to_do_register']] = []
    time_table_list: Optional[List['time_table_register']] = []
    result_list: Optional[List['result_register']] = []


class planner_data(BaseModel):
    date: date
    user_id: str
    to_do_list: List['to_do_data'] = []
    time_table_list: List['time_table_data'] = []
    result_list: List['result_register'] = []
    study_time: Optional[int] = 0

