from pydantic import BaseModel, validator
from typing import List, Optional, Set
import re

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
    
class time_table(BaseModel):
    subject: str
    time: Optional[List[unit_time]] = []

    @validator('time', pre=True, each_item=True)
    def time_validator(cls, v):
        if isinstance(v, unit_time):
            return v
        pattern = re.compile(r'^(2[0-3]|1[0-9]|[0-9]):[0-5]$')
        if not pattern.match(str(v)):
            raise ValueError("Time must be in the format of 'hour:position'")
        return unit_time(v)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_dict(cls, data):
        return cls(
            subject=data["subject"],
            time=list([unit_time(t) for t in data["time"]])
        )
    
    def to_dict(self):
        return {
            "subject": self.subject,
            "time": [str(t) for t in self.time]
        }