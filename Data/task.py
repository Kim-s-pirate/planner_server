from pydantic import BaseModel
from typing import Optional


class task(BaseModel):
    title: str
    memo: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            memo=data["memo"]
        )

    def to_dict(self):
        return {
            "title": self.title,
            "memo": self.memo
        }

