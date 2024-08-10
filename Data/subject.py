from pydantic import BaseModel
from typing import Optional

class subject_register(BaseModel):
    title: str

class subject_data(BaseModel):
    id: str
    user_id: str
    title: str
    color: str

class subject_title(BaseModel):
    title: str

class subject_color(BaseModel):
    color: str