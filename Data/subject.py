from pydantic import BaseModel
from typing import Optional

class subject_register(BaseModel):
    subject: str

class subject_data(BaseModel):
    id: str
    user_id: str
    subject: str
    color: str