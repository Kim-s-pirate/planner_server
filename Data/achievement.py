from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class achievement_request(BaseModel):
    start_date: date
    end_date: date

class achievement(BaseModel):
    book_id: str
    progress: Optional[float] = 0.0

class achievement_date(BaseModel):
    date: date