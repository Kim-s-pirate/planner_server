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
async def book_register(request: Request, book_data: book_register):
    try:
        token = authenticate_user(request)
        book_data = book_service.to_book_db(book_data, token["userid"])
        result = book_service.create_book(book_data)
        if result == False:
            return JSONResponse(status_code=409, content={"message": "Book already exists"})
        return JSONResponse(status_code=201, content={"message": "Book registered successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=409, content={"message": "Book registration failed"})
    finally:
        db.commit()

@router.get("/book/{bookid}")
async def book_info(request: Request, bookid: str):
    try:
        token = authenticate_user(request)
        if book_service.find_book_by_id(bookid).userid != token["userid"]:
            return JSONResponse(status_code=401, content={"message": "You are not authorized to view this book"})
        book = book_service.find_book_by_id(bookid)
        if book == None:
            return JSONResponse(status_code=200, content={"message": "Book not found"})
        return JSONResponse(status_code=200, content={"book":book_service.to_book_data(book).__dict__})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the book"})
    
@router.get("/book_list")
async def book_list(request: Request):
    try:
        token = authenticate_user(request)
        books = db.query(book).filter(book.userid == token["userid"]).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the book list"})
    
@router.delete("/book_delete/{title}")
async def book_delete(request: Request, title: str):
    try:
        token = authenticate_user(request)
        if book_service.find_book_by_title(title, token["userid"]).userid != token["userid"]:
            return JSONResponse(status_code=401, content={"message": "You are not authorized to delete this book"})
        book_service.delete_book(title, token["userid"])
        return JSONResponse(status_code=200, content={"message": "Book deleted successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error while deleting the book"})

@router.get("/active_book_list")
async def active_book_list(request: Request):
    try:
        token = authenticate_user(request)
        books = db.query(book).filter(book.userid == token["userid"], book.status == True).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the book list"})
    
@router.get("/inactive_book_list")
async def inactive_book_list(request: Request):
    try:
        token = authenticate_user(request)
        books = db.query(book).filter(book.userid == token["userid"], book.status == False).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the book list"})
    
@router.post("/edit_book/{title}")
async def edit_book(request: Request, book_data: book_edit, title: str):
    try:
        token = authenticate_user(request)
        book = book_service.edit_book(book_data, token["userid"], title)
        if book == False:
            return JSONResponse(status_code=302, content={"message": "Book title already exists"})
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=409, content={"message": e.__str__()})
    finally:
        db.commit()