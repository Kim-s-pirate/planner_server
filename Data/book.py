from pydantic import BaseModel
from typing import Optional

class book_register(BaseModel):
    title: str
    start_page: int
    end_page: int
    memo: str
    status: Optional[bool] = True
    subject: Optional[str] = None

class book_data(BaseModel):
    id: int
    userid: str
    title: str
    start_page: int
    end_page: int
    memo: str
    status: bool
    subject: Optional[str] = None

class book_edit(BaseModel):
    title: str
    start_page: int
    end_page: int
    memo: str
    status: bool
    subject: Optional[str] = None