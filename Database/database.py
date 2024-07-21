# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
TEMP_URL = "mysql+mysqlconnector://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + ":3306/"
DATABASE_URL = "mysql+mysqlconnector://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + ":3306/planner"
temp_engine = create_engine(TEMP_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()

def create_database():
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS planner"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
