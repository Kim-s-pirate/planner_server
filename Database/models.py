import random
import uuid
from sqlalchemy import JSON, DateTime, ForeignKey, Column, Index, Integer, PrimaryKeyConstraint, String, Time, Boolean, UniqueConstraint, event
from sqlalchemy.orm import relationship
from Database.database import Base, db, engine, get_db
from datetime import datetime, timezone, timedelta
import hashlib

def hash_id():
    unique_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + str(uuid.uuid4())
    return hashlib.sha256(unique_string.encode()).hexdigest()

class BaseEntity(Base):
    __abstract__ = True
    is_deleted = Column(Boolean, default = False)
    created_at = Column(DateTime, default = datetime.now)
    updated_at = Column(DateTime, default = datetime.now, onupdate = datetime.now)


class user(BaseEntity): # id
    __tablename__ = "users"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    userid = Column(String(50), index=True, unique=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), index=True, unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    oauth = Column(Boolean, default=False, nullable=False)
    sound_setting = Column(Integer, default=0, nullable=False)
    books = relationship("book", back_populates="user", cascade="all, delete, save-update")
    subjects = relationship("subject", back_populates="user", cascade="all, delete, save-update")
    schedules = relationship("schedule", back_populates="user", cascade="all, delete, save-update")
    goals = relationship("goal", back_populates="user", cascade="all, delete, save-update")
    time_table = relationship("time_table", back_populates="user", cascade="all, delete, save-update")
    to_do = relationship("to_do", back_populates="user", cascade="all, delete, save-update")
    result = relationship("result", back_populates="user", cascade="all, delete, save-update")
    d_day = relationship("d_day", back_populates="user", cascade="all, delete, save-update")
    #내가 보기엔 굳이 userid랑 FK로 연결할 필요가 없어보임. 그냥 id로 연결해도 될듯
    #하지만 userid를 항상 쿼리해야해서 시간 복잡도가 올라갈 수도 있어서 user를 제외한 참조들을 id를 쓰는 것이 좋아보임

class log(BaseEntity):
    __tablename__ = "logs"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    log = Column(String(150), nullable=False)
    time = Column(Time, default=datetime.now, nullable=False)  # 현재 시간을 기본값으로 설정

class to_do(BaseEntity): # id
    __tablename__ = "to_do"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    date = Column(String(50), index=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    title = Column(String(50), nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    book_id = Column(String(100), ForeignKey('books.id', ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    book = relationship("book", back_populates="to_do", foreign_keys=[book_id])#이거 코드 필요한지 확인 필요
    user = relationship("user", back_populates="to_do")
    __table_args__ = (UniqueConstraint('user_id', 'title', 'date', 'book_id', name='unique_user_id_title_date_book_id'),)#이걸 책까지 포함할지 말지는 고민해봐야함

class book(BaseEntity): # id
    __tablename__ = "books"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False)
    title = Column(String(50), nullable=False, index=True)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    memo = Column(String(150), nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    subject_id = Column(String(100), ForeignKey('subjects.id', ondelete="SET NULL", onupdate="CASCADE"), index=True, nullable=True)
    initial = Column(String(300), nullable=True)
    user = relationship("user", back_populates="books") 
    subject = relationship("subject", back_populates="books")
    to_do = relationship("to_do", back_populates="book", foreign_keys=[to_do.book_id], cascade="all, delete, save-update")
    result = relationship("result", back_populates="book", cascade="all, delete, save-update")
    __table_args__ = (UniqueConstraint('user_id', 'title', name='unique_user_id_title'),)

def set_initial(mapper, connenction, target):
    from Service.book_service import book_service
    if target.title:
        target.initial = book_service.convert_text_to_initial(target.title)

event.listen(book, 'before_insert', set_initial)

class subject(BaseEntity):
    __tablename__ = "subjects"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    title = Column(String(50), index=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    color = Column(String(7), nullable=False)
    user = relationship("user", back_populates="subjects")
    books = relationship("book", back_populates="subject")
    time_table = relationship("time_table", back_populates="subject")
    __table_args__ = (UniqueConstraint('user_id', 'title', name='unique_user_id_title'),)

    def __init__(self, title, user_id, color=None):
        db = get_db()
        from Service.subject_service import subject_service
        self.title = title
        self.user_id = user_id
        self.color = color if color else subject_service.random_color(user_id, db)
        
class schedule(BaseEntity):#id
    __tablename__ = "calender"
    date = Column(String(50), primary_key=True, index=True, unique=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    task_list = Column(JSON, nullable=False)
    user = relationship("user", back_populates="schedules")

class goal(BaseEntity):#id
    __tablename__ = "goals"
    year = Column(Integer, primary_key=True, index=True, nullable=False)
    month = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    goal = Column(String(500), nullable=True)
    user = relationship("user", back_populates="goals")

class time_table(BaseEntity): # id
    __tablename__ = "time_table"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    date = Column(String(50), index=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    subject_id = Column(String(100), ForeignKey('subjects.id', ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    time = Column(JSON, nullable=False)
    user = relationship("user", back_populates="time_table")
    subject = relationship("subject", back_populates="time_table")
    __table_args__ = (UniqueConstraint('user_id', 'date', 'subject_id', name='unique_user_id_date_subject_id'),)

class result(BaseEntity):
    __tablename__ = "results"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    date = Column(String(50), index=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    book_id = Column(String(100), ForeignKey('books.id', ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    page = Column(JSON, nullable=False)
    book = relationship("book", back_populates="result")
    user = relationship("user", back_populates="result")
    __table_args__ = (UniqueConstraint('user_id', 'date', 'book_id', name='unique_user_id_date_book_id'),)
        
class verification(BaseEntity):
    __tablename__ = "verifications"
    email = Column(String(100), index=True, unique=True, nullable=False, primary_key=True)
    code = Column(String(10), nullable=False)
    time = Column(DateTime, default=datetime.now, nullable=False)  # 현재 시간을 기본값으로 설정
    expire_time = Column(DateTime, default=lambda: datetime.now() + timedelta(minutes=30), nullable=False)

class state(BaseEntity):
    __tablename__ = "states"
    email = Column(String(100), index=True, unique=True, nullable=False, primary_key=True)
    state = Column(String(100), nullable=False)

class d_day(BaseEntity):
    __tablename__ = "d_day"
    id = Column(String(100), default=hash_id, primary_key=True, index=True, unique=True, nullable=False)
    user_id = Column(String(100), ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True, nullable=False)
    date = Column(String(50), nullable=False)
    title = Column(String(50), nullable=False)
    star = Column(Boolean, default=False, nullable=False)
    user = relationship("user", back_populates="d_day")
    __table_args__ = (UniqueConstraint('user_id', 'date', 'title', name='unique_user_id_date_title'),)