from pydantic import BaseModel, field_validator, validator
from typing import List, Optional, Set
import re
from datetime import date

from Service.subject_service import *
#6:0
#0:0
#23:0

class unit_time:
    hour: int
    position: int
    def __init__(self, string: str):
        self.hour = int(string.split(":")[0])
        self.position = int(string.split(":")[1])

    def __str__(self):
        return f"{self.hour}:{self.position}"
    
    def __repr__(self):
        return f"{self.hour}:{self.position}"
    
    def __eq__(self, other):
        return self.hour == other.hour and self.position == other.position
    
    def __hash__(self):
        return hash((self.hour, self.position))
    
    def __lt__(self, other):
        if self.hour == other.hour:
            return self.position < other.position
        return self.hour < other.hour
    
    def __le__(self, other):
        if self.hour == other.hour:
            return self.position <= other.position
        return self.hour <= other.hour
    
    def __gt__(self, other):
        if self.hour == other.hour:
            return self.position > other.position
        return self.hour > other.hour
    
    def __ge__(self, other):
        if self.hour == other.hour:
            return self.position >= other.position
        return self.hour >= other.hour
    
    def from_string(cls, string):
        return cls(string)
    
    def to_string(cls):
        return str(cls)
    
class time_table_register(BaseModel):
    date: date
    subject_id: str
    time: Optional[List[unit_time]] = []

    def __hash__(self):
        return hash((self.date, self.subject_id, tuple(sorted(self.time))))
    
    def __eq__(self, other):
        return self.date == other.date and self.subject_id == other.subject_id and set(self.time) == set(other.time)

    class Config:
        arbitrary_types_allowed = True

    @field_validator('time', mode='before')
    def parse_time(cls, v):
        if v is None:
            return v
        return [unit_time(item) if isinstance(item, str) else item for item in v]
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            date=data["date"],
            subject_id=data["subject_id"],
            time=list([unit_time(t) for t in data["time"]])
        )
    
    def to_dict(self):
        return {
            "date": self.date,
            "subject_id": self.subject_id,
            "time": [str(t) for t in self.time]
        }

class time_table_data(BaseModel):
    date: date
    userid: str
    subject_id: str
    time: Optional[List[unit_time]] = []

    def __hash__(self):
        return hash((self.date, self.subject_id, tuple(sorted(self.time))))
    
    def __eq__(self, other):
        return self.date == other.date and self.subject_id == other.subject_id and set(self.time) == set(other.time)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_dict(cls, data):
        return cls(
            date=data["date"],
            subject_id=data["subject_id"],
            time=list([unit_time(t) for t in data["time"]])
        )
    
    def to_dict(self):
        return {
            "date": self.date,
            "subject_id": self.subject_id,
            "time": [str(t) for t in self.time]
        }
    
    @field_validator('time', mode='before')
    def parse_time(cls, v):
        if v is None:
            return v
        return [unit_time(item) if isinstance(item, str) else item for item in v]