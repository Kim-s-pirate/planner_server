from contextlib import asynccontextmanager
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Database.database import db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.status import *
import uvicorn
from Database.database import create_database
from Router import register, login, main_page, book, subject, calendar, planner
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

create_database()
app = FastAPI()

load_dotenv("../.env")
secret = os.getenv("secret")

app.add_middleware(SessionMiddleware, secret_key=secret, max_age=10800)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(main_page.router)
app.include_router(book.router)
app.include_router(subject.router)
app.include_router(calendar.router)
app.include_router(planner.router)

# CORS
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=1500, reload=True)