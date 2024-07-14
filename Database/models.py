from sqlalchemy import ForeignKey, Column, Integer, String, Time, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from Database.database import Base, db, engine
from datetime import datetime

class user(Base):
    __tablename__ = "users"
    userid = Column(String(50), primary_key=True, index=True, unique=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), index=True, unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    books = relationship("book", back_populates="user", cascade="all, delete")
    subjects = relationship("subject", back_populates="user", cascade="all, delete")
    schedules = relationship("schedule", back_populates="user", cascade="all, delete")
    goals = relationship("goal", back_populates="user", cascade="all, delete")

class log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
    userid = Column(String(50), nullable=False)
    time = Column(Time, default=datetime.now, nullable=False)  # 현재 시간을 기본값으로 설정
    log = Column(String(150), nullable=False)

class book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE"), nullable=False)
    title = Column(String(50), nullable=False)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    memo = Column(String(150), nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    subject = Column(String(50), ForeignKey('subjects.subject', ondelete="SET NULL"), nullable=True)
    user = relationship("user", back_populates="books")
    subject_relation = relationship("subject", back_populates="books")

class subject(Base):
    __tablename__ = "subjects"
    subject = Column(String(50), primary_key=True, index=True, unique=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE"), nullable=False)
    user = relationship("user", back_populates="subjects")
    books = relationship("book", back_populates="subject_relation")

class schedule(Base):
    __tablename__ = "calender"
    date = Column(String(50), primary_key=True, index=True, unique=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE"), nullable=False)
    schedule = Column(String(300), nullable=False)
    user = relationship("user", back_populates="schedules")

class goal(Base):
    __tablename__ = "goals"
    year = Column(Integer, primary_key=True, index=True, nullable=False)
    month = Column(Integer, primary_key=True, index=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE"), nullable=False)
    month_goal = Column(String(300), nullable=True)
    week_goal = Column(String(500), nullable=True)
    user = relationship("user", back_populates="goals")