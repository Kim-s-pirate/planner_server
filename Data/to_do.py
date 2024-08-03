from pydantic import BaseModel
from typing import Optional
from datetime import date

class to_do_register(BaseModel):
    date: date
    title: str
    status: Optional[bool] = True
    book_title: Optional[str] = None
    subject: Optional[str] = None

    def __hash__(self):
        return hash((self.date, self.title, self.status, self.book_title, self.subject))
    
    def __eq__(self, other):
        return self.date == other.date and self.title == other.title and self.status == other.status and self.book_title == other.book_title and self.subject == other.subject


class to_do_data(BaseModel):
    date: date
    userid: str
    title: str
    status: Optional[bool] = True
    book_title: Optional[str] = None
    subject: Optional[str] = None

    def __hash__(self):
        return hash((self.date, self.title, self.status, self.book_title, self.subject))
    
    def __eq__(self, other):
        return self.date == other.date and self.title == other.title and self.status == other.status and self.book_title == other.book_title and self.subject == other.subject
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            date=data["date"],
            title=data["title"],
            status=data["status"],
            book_title=data["book_title"],
            subject=data["subject"]
        )
    
    def to_dict(self):
        return {
            "date": self.date,
            "title": self.title,
            "status": self.status,
            "book_title": self.book_title,
            "subject": self.subject
        }