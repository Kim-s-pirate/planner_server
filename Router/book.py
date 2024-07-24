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
            return JSONResponse(status_code=302, content={"message": "Book already exists"})
        return JSONResponse(status_code=201, content={"message": "Book registered successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"message": "Book registration failed"})
    finally:
        db.commit()

#duplicate_book
@router.get("/duplicate_book")
async def duplicate_subject(request: Request, booktitle: str):
    try:
        token = authenticate_user(request)
        userid = token["userid"]
        found_book = book_service.find_book_by_title(booktitle, userid)
        if found_book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})# modify?? : subject can be created
        return JSONResponse(status_code=409, content={"message": f"Book '{booktitle}' already exists"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})


#이부분 책 검색에 대한 검색 기준을 확립할 필요가 있음
#초성으로만 검색할 수 있는 기능 추가하면 좋음

#추가: 서브젝트 검색 기능
#추가: 이름 일부만으로도 검색할 수 있는 기능
@router.get("/book/{booktitle}")
async def book_info(request: Request, booktitle: str):
    try:
        token = authenticate_user(request)
        if book_service.find_book_by_title(booktitle, token["userid"]).userid != token["userid"]:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        book = book_service.find_book_by_title(booktitle, token["userid"])
        if book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        return JSONResponse(status_code=200, content={"book":book_service.to_book_data(book).__dict__})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})
    
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
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})
    
@router.delete("/book_delete/{title}")
async def book_delete(request: Request, title: str):
    try:
        token = authenticate_user(request)
        if book_service.find_book_by_title(title, token["userid"]).userid != token["userid"]:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this book"})
        book_service.delete_book(title, token["userid"])
        return JSONResponse(status_code=200, content={"message": "Book deleted successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the book"})

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
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})
    
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
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})
    
@router.post("/edit_book/{title}")
async def edit_book(request: Request, book_data: book_edit, title: str):
    try:
        token = authenticate_user(request)
        book = book_service.edit_book(book_data, token["userid"], title)
        if book == False:
            return JSONResponse(status_code=302, content={"message": "Book title already exists"})
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=500, content={"message": e.__str__()})
    finally:
        db.commit()

@router.get("/book_list/{subject}")
async def book_list_by_subject(request: Request, subject: str):
    try:
        token = authenticate_user(request)
        books = db.query(book).filter(book.userid == token["userid"], book.subject == subject).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except TokenNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except TokenVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})