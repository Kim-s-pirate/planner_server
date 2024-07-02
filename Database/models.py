from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.sql.functions import current_time
from Database.database import Base, db, engine
from datetime import datetime

class user(Base):
    __tablename__ = "users"
    userid = Column(String(50), primary_key=True, index=True, unique=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), index=True, unique=True, nullable=False)
    password = Column(String(100), nullable=False)

class log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
    userid = Column(String(50), nullable=False)
    time = Column(Time, default=datetime.now, nullable=False)  # 현재 시간을 기본값으로 설정
    log = Column(String(150), nullable=False)