from pydantic import BaseModel

class book_register(BaseModel):
    title: str
    start_page: int
    end_page: int
    memo: str

class book_data(BaseModel):
    id: int
    userid: str
    title: str
    start_page: int
    end_page: int
    memo: str