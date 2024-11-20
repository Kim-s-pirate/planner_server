import os
import random
import secrets
from aiosmtplib import send
from fastapi import FastAPI, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List
from fastapi import APIRouter
from Data.email import *
from Database.database import get_db
from Database.models import hash_id
from Service.email_service import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from Service.limiter import limiter
template_dir = os.path.join(os.path.dirname(__file__), "../Resource")
env = Environment(loader=FileSystemLoader(template_dir))
router = APIRouter(tags=["email"], prefix="/email")
load_dotenv(".env")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("email")
SMTP_PASSWORD = os.getenv("password")

email = os.getenv("email")
password = os.getenv("password")
gmail_user = email
gmail_password = password

async def send_email_background_task(message: str):
    await send(
        message,
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASSWORD
    )

@router.post("/send_verification_email", summary="이메일 전송", description="회원가입 이메일 전송", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Email sent successfully!"}}}},
    500: {"description": "이메일 전송 실패", "content": {"application/json": {"example": {"message": "There was some error while sending the email"}}}}
})
@limiter.limit("3/1minutes")
async def send_email(request: Request, email: email_request, background_tasks: BackgroundTasks):
    with get_db() as db:
        try:
            message = MIMEMultipart()
            message["From"] = SMTP_USER
            message["To"] = email.email
            message["Subject"] = "회원가입 이메일 인증"
            email = email.email
            verification_code = ''.join(random.choices('0123456789', k=6))
            template = env.get_template("email_verification_form.html")
            body = template.render(verification_code=verification_code)
            message.attach(MIMEText(body, "html"))
            background_tasks.add_task(send_email_background_task, message)
            email_service.register_verification(email, verification_code, db)
            return JSONResponse(status_code=200, content={"message": "Email sent successfully!"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "There was some error while sending the email"})

@router.post("/verify/code", summary="이메일 인증번호 인증", description="회원가입 이메일 인증번호 인증", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Verification code is correct", "state": "some_state"}}}},
    400: {"description": "인증번호 오류", "content": {"application/json": {"example": {"message": "Verification code is incorrect"}}}},
    404: {"description": "이메일 없음", "content": {"application/json": {"example": {"message": "Email not found"}}}},
    500: {"description": "서버 에러", "content": {"application/json": {"example": {"message": "There was some error while verifying the code"}}}}
})
async def verification_code(verify: email_verification):
    with get_db() as db:
        try:
            email = verify.email
            code = verify.code
            found = email_service.find_verification_by_email(email, db)
            if found is None:
                return JSONResponse(status_code=404, content={"message": "Email not found"})
            if found.code != code:
                return JSONResponse(status_code=400, content={"message": "Verification code is incorrect"})
            state = hash_id()
            email_service.register_state(verify.email, state, db)
            return JSONResponse(status_code=200, content={"message": "Verification code is correct", "state": state})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "There was some error while verifying the code"})
