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

class book_title(BaseModel):
    title: str

class book_subject_id(BaseModel):
    subject_id: str

class book_page(BaseModel):
    start_page: int
    end_page: int

class book_memo(BaseModel):
    memo: str

class book_status(BaseModel):
    status: bool