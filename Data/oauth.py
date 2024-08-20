from pydantic import BaseModel
from typing import Optional

class naver_data(BaseModel):
    code: str
    state: str