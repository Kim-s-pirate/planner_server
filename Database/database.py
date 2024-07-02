# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+mysqlconnector://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + ":3306/planner"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()
def create_database():
    Base.metadata.create_all(bind=engine)