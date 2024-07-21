from pydantic import BaseModel

class user_register(BaseModel):
    userid: str
    username: str
    email: str
    password: str

class user_login(BaseModel):
    email: str
    password: str

class email(BaseModel):
    email: str

class userid(BaseModel):
    userid: str

class user_edit(BaseModel):
    userid: str
    username: str