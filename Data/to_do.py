from pydantic import BaseModel
from typing import Optional

class to_do(BaseModel):
    title: str
    status: Optional[bool] = True
    book_title: Optional[str] = None
    subject: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            status=data["status"],
            book_title=data["book_title"],
            subject=data["subject"]
        )
    
    def to_dict(self):
        return {
            "title": self.title,
            "status": self.status,
            "book_title": self.book_title,
            "subject": self.subject
        }

