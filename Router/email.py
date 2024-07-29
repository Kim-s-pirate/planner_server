from fastapi import FastAPI, Query, Request
from pydantic import BaseModel, EmailStr
from typing import List
from fastapi import APIRouter
import yagmail

router = APIRouter()
#This code test is done. It works well.
# -> need to be make real email, app password

gmail_user = 'email'
gmail_password = 'app password'

# 수신자 이메일과 메시지 내용
subject = 'Test Email'
body = 'This is a test email sent using yagmail.'

@router.post("/send-email")
async def send_email(request: Request):
    request = await request.json()
    email_address = request['email']
    yag = yagmail.SMTP(user=gmail_user, password=gmail_password)

    # 이메일 전송
    yag.send(
        to=email_address,
        subject=subject,
        contents=body,
    )

    return {"message": "Email sent successfully!"}

