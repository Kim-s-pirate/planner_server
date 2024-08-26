from pydantic import BaseModel
from typing import Optional

class user_register(BaseModel):
    userid: str
    username: str
    email: str
    password: str
    state: Optional[str] = None

class user_login(BaseModel):
    email: str
    password:str

class user_email(BaseModel):
    email: str

class user_userid(BaseModel):
    userid: str

class user_username(BaseModel):
    username: str

class user_data(BaseModel):
    id: str
    userid: str
    username: str
    email: str

class user_password(BaseModel):
    password: str