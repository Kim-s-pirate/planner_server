import os
import random
import secrets
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
from dotenv import load_dotenv

templates = Jinja2Templates(directory="Resource")
router = APIRouter()
#This code test is done. It works well.
# -> need to be make real email, app password

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
        
        email = email.email
        subject = "회원가입 이메일 인증"
        verification_code = ''.join(random.choices('0123456789', k=6))
        body = templates.get_template("email_verification_form.html").render(request=request, verification_code=verification_code)
        yag = yagmail.SMTP(user=gmail_user, password=gmail_password)
        yag.send(
            to=email,
            subject=subject,
            contents=body,
        )
        email_service.register_verification(email, verification_code, db)
        return JSONResponse(status_code=200, content={"message": "Email sent successfully"})
    except Exception as e:
        raise e
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "There was some error while sending the email"})
    finally:
        db.commit()

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
            return JSONResponse(status_code=401, content={"message": "Verification code is incorrect"})
        state = hash_id()
        email_service.register_state(verify.email, state, db)


        return JSONResponse(status_code=200, content={"message": "Verification code is correct", "state": state})
    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while verifying the code"})
    finally:
        db.close()
