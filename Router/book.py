from fastapi.responses import JSONResponse
from Database.database import db
from fastapi import APIRouter
from starlette.status import *
from jose import JWTError, jwt
from Service.authorization_service import *
import os
from dotenv import load_dotenv
from fastapi import Request
from Data.book import *
from Service.book_service import *

router = APIRouter()
load_dotenv("../.env")
secret = os.getenv("secret")

@router.post("/book_register")
def book_register(request: Request, book_data: book_register):
    try:
        token = get_token(request)
        if token == False:
            return JSONResponse(status_code=400, content={"message": "Token not found"})
        verify = verify_token(token)
        if verify == False:
            return JSONResponse(status_code=400, content={"message": "Token verification failed"})
        token = decode_token(token)
        book_data = book_service.to_book_db(book_data, token["userid"])
        book_service.create_book(book_data)
        return JSONResponse(status_code=201, content={"message": "Book registered successfully"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=409, content={"message": "Book registration failed"})
    finally:
        db.commit()