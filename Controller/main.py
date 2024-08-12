from contextlib import asynccontextmanager
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Database.database import db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.status import *
import uvicorn
from Database.database import create_database, engine
from Router import register, login, main_page, book, subject, calendar, planner, email, achievement
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
create_database()
from Service.email_service import email_service
import threading
import schedule

load_dotenv("../.env")
secret = os.getenv("secret")


schedule.every(10).minutes.do(lambda: email_service.delete_expired_verification(db))

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

app = FastAPI()



app.add_middleware(SessionMiddleware, secret_key=secret, max_age=10800)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(main_page.router)
app.include_router(book.router)
app.include_router(subject.router)
app.include_router(calendar.router)
app.include_router(planner.router)
app.include_router(email.router)
app.include_router(achievement.router)

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
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    uvicorn.run("main:app", host="0.0.0.0", port=1500, reload=True, ssl_keyfile="C:\\Users\\gon13\\Desktop\\planner_server\\Controller\\key.pem", ssl_certfile="C:\\Users\\gon13\\Desktop\\planner_server\\Controller\\cert.pem")