from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import get_db
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
        db = get_db()
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        userid = AuthorizationService.verify_session(request, db)
        book_data = book_service.to_book_db(book_data, userid)
        result = book_service.create_book(book_data, db)
        if result == False:
            return JSONResponse(status_code=302, content={"message": "Book already exists"})
        return JSONResponse(status_code=201, content={"message": "Book registered successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"message": "Book registration failed"})
    finally:
        db.commit()
        db.close()


#과목이 없는 경우 에러가 걸림

#duplicate_book
@router.get("/duplicate_book")
async def duplicate_subject(request: Request, booktitle: str):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        userid = userid
        found_book = book_service.find_book_by_title(booktitle, userid, db)
        if found_book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})# modify?? : subject can be created
        return JSONResponse(status_code=409, content={"message": f"Book '{booktitle}' already exists"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})
    finally:
        db.close()


#이부분 책 검색에 대한 검색 기준을 확립할 필요가 있음
#초성으로만 검색할 수 있는 기능 추가하면 좋음

#추가: 서브젝트 검색 기능
#추가: 이름 일부만으로도 검색할 수 있는 기능
#해당 기능에서 현재 문제 발생

@router.get("/book_subject/{booktitle}")
async def book_subject(request: Request, booktitle: str):
    try:
        userid = AuthorizationService.verify_session(request)
        if book_service.find_book_by_title(booktitle, userid).userid != userid:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        book = book_service.find_book_by_title(booktitle, userid)
        if book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        return JSONResponse(status_code=200, content={"subject": book_service.to_book_data(book).__dict__["subject"]})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})

@router.get("/book/{booktitle}")
async def book_info(request: Request, booktitle: str):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        if book_service.find_book_by_title(booktitle, userid).userid != userid:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        book = book_service.find_book_by_title(booktitle, userid, db)
        if book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        return JSONResponse(status_code=200, content={"book":book_service.to_book_data(book).__dict__})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})
    finally:
        db.close()


# 초성 검색 기능
@router.get("/book_initial/{initial}")
async def book_initial(request: Request, initial: str):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        books = book_service.find_book_by_initial(initial, userid, db)
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the book list"})
    finally:
        db.close()

@router.get("/book_list")
async def book_list(request: Request):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        books = db.query(book).filter(book.userid == userid).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})
    finally:
        db.close()
    
@router.delete("/book_delete/{title}")
async def book_delete(request: Request, title: str):
    try:
        db = get_db()
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        userid = AuthorizationService.verify_session(request, db)
        if book_service.find_book_by_title(title, userid, db).userid != userid:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this book"})
        book_service.delete_book(title, userid, db)
        return JSONResponse(status_code=200, content={"message": "Book deleted successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the book"})
    finally:
        db.commit()
        db.close()

@router.get("/active_book_list")
async def active_book_list(request: Request):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        #여기 서비스 코드로 보내야함
        books = db.query(book).filter(book.userid == userid, book.status == True).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})
    finally:
        db.close()
    
@router.get("/inactive_book_list")
async def inactive_book_list(request: Request):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        books = db.query(book).filter(book.userid == userid, book.status == False).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})
    finally:
        db.close()
    
@router.post("/edit_book/{title}")
async def edit_book(request: Request, book_data: book_edit, title: str):
    try:
        db = get_db()
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        userid = AuthorizationService.verify_session(request, db)
        book = book_service.edit_book(book_data, userid, title, db)
        if book == False:
            return JSONResponse(status_code=302, content={"message": "Book title already exists"})
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=500, content={"message": e.__str__()})
    finally:
        db.commit()
        db.close()

@router.get("/book_list/{subject}")
async def book_list_by_subject(request: Request, subject: str):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        books = db.query(book).filter(book.userid == userid, book.subject == subject).all()
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"books": book_list})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})
    finally:
        db.close()
    
@router.get("/book/{subject}") #이거 이름 수정하고 과목에 대한 엔드포인트로 변경
async def get_subject_book(request: Request, subject: str):
    try:
        db = get_db()
        userid = AuthorizationService.verify_session(request, db)
        found_book = book_service.find_book_by_subject(subject, userid, db)
        if found_book == []:
            return JSONResponse(status_code=404, content={"message": "Subject not found"})
        data = [book_service.to_book_data(book).dict() for book in found_book]
        return JSONResponse(status_code=200, content=data)
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Subject retrieval failed"})
    finally:
        db.close()