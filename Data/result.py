from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class result_register(BaseModel):
    date: date
    book_id: str
    page: Optional[List[int]] = []

    def __hash__(self):
        return hash((self.date, self.book_id, tuple(sorted(self.page))))
    
    def __eq__(self, other):
        return self.date == other.date and self.book_id == other.book_id and sorted(self.page) == sorted(other.page)

class result_data(BaseModel):
    date: date
    user_id: str
    book_id: str
    page: List[int] = []

    def __hash__(self):
        return hash((self.date, self.book_id, tuple(sorted(self.page))))
    
    def __eq__(self, other):
        return self.date == other.date and self.book_id == other.book_id and sorted(self.page) == sorted(other.page)