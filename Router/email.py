import os
import random
import secrets
from aiosmtplib import send
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List
from fastapi import APIRouter
import yagmail
from Data.email import *
from Database.database import get_db
from Database.models import hash_id
from Service.email_service import *
from fastapi.templating import Jinja2Templates
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
template_dir = os.path.join(os.path.dirname(__file__), "../Resource")
env = Environment(loader=FileSystemLoader(template_dir))
router = APIRouter()
#This code test is done. It works well.
# -> need to be make real email, app password

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("email")
SMTP_PASSWORD = os.getenv("password")

load_dotenv("../.env")
email = os.getenv("email")
password = os.getenv("password")
gmail_user = email
gmail_password = password

# 수신자 이메일과 메시지 내용
subject = 'Test Email'
body = 'This is a test email sent using yagmail.'


@router.post("/send_email/register")
async def send_email(request: Request, email: email_request):
    try:
        message = MIMEMultipart()
        #message["From"] = SMTP_USER
        message["To"] = email.email
        message["Subject"] = "회원가입 이메일 인증"
        email = email.email
        subject = "회원가입 이메일 인증"
        verification_code = ''.join(random.choices('0123456789', k=6))
        template = env.get_template("email_verification_form.html")
        body = template.render(verification_code=verification_code)
        message.attach(MIMEText(body, "html"))
        # 이메일 전송
        await send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD
        )
        
        return {"message": "Email sent successfully!"}
    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while sending the email"})
    #     body = templates.get_template("email_verification_form.html").render(request=request, verification_code=verification_code)
    #     yag = yagmail.SMTP(user=gmail_user, password=gmail_password)
    #     yag.send(
    #         to=email,
    #         subject=subject,
    #         contents=body,
    #     )
    #     email_service.register_verification(email, verification_code, db)
    #     return JSONResponse(status_code=200, content={"message": "Email sent successfully"})
    # except Exception as e:
    #     raise e
    #     db.rollback()
    #     return JSONResponse(status_code=500, content={"message": "There was some error while sending the email"})
    # finally:
    #     db.commit()


# async def send_email(to_email: str, subject: str, body: str):
#     # 이메일 메시지 생성
#     message = MIMEMultipart()
#     message["From"] = SMTP_USER
#     message["To"] = to_email
#     message["Subject"] = subject
#     message.attach(MIMEText(body, "plain"))

#     # 이메일 전송
#     await send(
#         message,
#         hostname=SMTP_SERVER,
#         port=SMTP_PORT,
#         start_tls=True,
#         username=SMTP_USER,
#         password=SMTP_PASSWORD
#     )
    
#     return {"message": "Email sent successfully!"}

@router.post("/verification_code")
async def verification_code(verify: email_verification):
    try:
        db = get_db()
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
    finally:
        db.close()
