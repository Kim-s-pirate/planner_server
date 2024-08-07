from pydantic import BaseModel
from typing import Optional

class book_register(BaseModel):
    title: str
    start_page: int
    end_page: int
    memo: str
    status: Optional[bool] = True
    subject_id: Optional[str] = None

class book_data(BaseModel):
    id: str
    user_id: str
    title: str
    start_page: int
    end_page: int
    memo: str
    status: bool
    subject_id: Optional[str] = None
    initial: Optional[str] = None

class book_edit(BaseModel):
    id: str
    title: str
    start_page: int
    end_page: int
    memo: str
    status: bool
    subject_id: Optional[str] = None