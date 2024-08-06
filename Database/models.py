import random
from sqlalchemy import JSON, DateTime, ForeignKey, Column, Index, Integer, PrimaryKeyConstraint, String, Time, Boolean, UniqueConstraint, event
from sqlalchemy.orm import relationship
from Database.database import Base, db, engine, get_db
from datetime import datetime, timezone
import hashlib

def hash_id():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()

class user(Base):
    __tablename__ = "users"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    userid = Column(String(50), index=True, unique=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), index=True, unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    books = relationship("book", back_populates="user", cascade="all, delete, save-update")
    subjects = relationship("subject", back_populates="user", cascade="all, delete, save-update")
    schedules = relationship("schedule", back_populates="user", cascade="all, delete, save-update")
    goals = relationship("goal", back_populates="user", cascade="all, delete, save-update")
    planner = relationship("planner", back_populates="user", cascade="all, delete, save-update")
    time_table = relationship("time_table", back_populates="user", cascade="all, delete, save-update")
    to_do = relationship("to_do", back_populates="user", cascade="all, delete, save-update")
    #내가 보기엔 굳이 userid랑 FK로 연결할 필요가 없어보임. 그냥 id로 연결해도 될듯
    #하지만 userid를 항상 쿼리해야해서 시간 복잡도가 올라갈 수도 있어서 user를 제외한 참조들을 id를 쓰는 것이 좋아보임

class log(Base):
    __tablename__ = "logs"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    userid = Column(String(50), nullable=False)
    time = Column(Time, default=datetime.now, nullable=False)  # 현재 시간을 기본값으로 설정
    log = Column(String(150), nullable=False)

class to_do(Base):
    __tablename__ = "to_do"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    date = Column(String(50), index=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    title = Column(String(50), nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    book_title = Column(String(50), ForeignKey('books.title', ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    subject= Column(String(50), ForeignKey('books.subject', ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    book = relationship("book", back_populates="to_do", foreign_keys=[book_title])
    user = relationship("user", back_populates="to_do")
    __table_args__ = (UniqueConstraint('userid', 'title', 'date', 'book_title', name='unique_userid_title_date_book_title'),)

class book(Base):
    __tablename__ = "books"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False)
    title = Column(String(50), nullable=False, index=True)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    memo = Column(String(150), nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    subject = Column(String(50), ForeignKey('subjects.subject', ondelete="SET NULL", onupdate="CASCADE"), index=True, nullable=True)
    initial = Column(String(300), nullable=True)
    user = relationship("user", back_populates="books") 
    subject_relation = relationship("subject", back_populates="books")
    to_do = relationship("to_do", back_populates="book", foreign_keys=[to_do.book_title], cascade="all, delete, save-update")
    __table_args__ = (UniqueConstraint('userid', 'title', name='unique_userid_title'),)

def set_initial(mapper, connenction, target):
    from Service.book_service import book_service
    if target.title:
        target.initial = book_service.convert_text_to_initial(target.title)

event.listen(book, 'before_insert', set_initial)



class subject(Base):
    __tablename__ = "subjects"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    subject = Column(String(50), index=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    color = Column(String(7), nullable=False)
    user = relationship("user", back_populates="subjects")
    books = relationship("book", back_populates="subject_relation")
    time_table = relationship("time_table", back_populates="subject_relation")
    __table_args__ = (UniqueConstraint('userid', 'subject', name='unique_userid_subject'),)

    def __init__(self, subject, userid, color=None):
        db = get_db()
        from Service.subject_service import subject_service
        self.subject = subject
        self.userid = userid
        self.color = color if color else subject_service.random_color(userid, db)
        
class schedule(Base):
    __tablename__ = "calender"
    date = Column(String(50), primary_key=True, index=True, unique=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    task_list = Column(JSON, nullable=False)
    user = relationship("user", back_populates="schedules")

class goal(Base):
    __tablename__ = "goals"
    year = Column(Integer, primary_key=True, index=True, nullable=False)
    month = Column(Integer, primary_key=True, index=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    month_goal = Column(String(300), nullable=True)
    week_goal = Column(String(500), nullable=True)
    user = relationship("user", back_populates="goals")

# class to_do(Base):
#     __tablename__ = "to_do"
#     id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
#     userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     title = Column(String(50), nullable=False)
#     status = Column(Boolean, default=True, nullable=False)
#     book_title = Column(String(50), nullable=True)
#     book_masking = Column(String(50), nullable=True)
#     subject = Column(String(50), nullable=True)
#     user = relationship("user", back_populates="to_do")
#     __table_args__ = (UniqueConstraint('userid', 'title', name='unique_userid_title'),)

# class planner(Base):
#     __tablename__ = "planner"
#     id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
#     userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     date = Column(String(50), nullable=False)
#     to_do_list = Column(JSON, nullable=True)
#     time_table_list = Column(JSON, nullable=True)
#     user = relationship("user", back_populates="planner")
#     __table_args__ = (UniqueConstraint('userid', 'date', name='unique_userid_date'),)

class planner(Base):
    __tablename__ = "planner"
    date = Column(String(50), index=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    study_time = Column(Integer, nullable=False, default=0)
    #해당 컬럼에 트리거 필요
    user = relationship("user", back_populates="planner")
    __table_args__ = (PrimaryKeyConstraint('date', 'userid'), UniqueConstraint('userid', 'date', name='unique_userid_date'),)

class time_table(Base):
    __tablename__ = "time_table"
    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
    date = Column(String(50), index=True, nullable=False)
    userid = Column(String(50), ForeignKey('users.userid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    subject = Column(String(50), ForeignKey('subjects.subject', ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    time = Column(JSON, nullable=False)
    user = relationship("user", back_populates="time_table")
    subject_relation = relationship("subject", back_populates="time_table")
    __table_args__ = (UniqueConstraint('userid', 'date', 'subject', name='unique_userid_date_subject'),)
        
class verification(Base):
    __tablename__ = "verifications"
    email = Column(String(100), index=True, unique=True, nullable=False, primary_key=True)
    code = Column(String(10), nullable=False)
    time = Column(DateTime, default=datetime.now, nullable=False)  # 현재 시간을 기본값으로 설정