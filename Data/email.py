from pydantic import BaseModel
from typing import Optional

class email_request(BaseModel):
    email: str

class code(BaseModel):
    code: str

class email_verification(BaseModel):
    email: str
    code: str