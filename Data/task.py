from pydantic import BaseModel
from typing import Optional


class task(BaseModel):
    title: str
    memo: Optional[str] = None
    color: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            memo=data["memo"],
            color=data["color"]
        )

    def to_dict(self):
        return {
            "title": self.title,
            "memo": self.memo,
            "color": self.color
        }

