from pydantic import BaseModel
from typing import Optional
from datetime import date

class to_do_register(BaseModel):
    date: date
    title: str
    status: Optional[bool] = True
    book_id: Optional[str] = None
    subject_id: Optional[str] = None

    def __hash__(self):
        return hash((self.date, self.title, self.status, self.book_id, self.subject_id))
    
    def __eq__(self, other):
        return self.date == other.date and self.title == other.title and self.status == other.status and self.book_id == other.book_id and self.subject_id == other.subject_id


class to_do_data(BaseModel):
    date: date
    user_id: str
    title: str
    status: Optional[bool] = True
    book_id: Optional[str] = None
    subject_id: Optional[str] = None

    def __hash__(self):
        return hash((self.date, self.title, self.status, self.book_id, self.subject_id))
    
    def __eq__(self, other):
        return self.date == other.date and self.title == other.title and self.status == other.status and self.book_id == other.book_id and self.subject_id == other.subject_id
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            date=data["date"],
            title=data["title"],
            status=data["status"],
            book_id=data["book_id"],
            subject_id=data["subject_id"]
        )
    
    def to_dict(self):
        return {
            "date": self.date,
            "title": self.title,
            "status": self.status,
            "book_id": self.book_id,
            "subject_id": self.subject_id
        }