from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import get_db, rollback_to_savepoint
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


@router.post("/book_register")
async def book_register(request: Request, book_data: book_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        book_data = book_service.to_book_db(book_data, user_id)
        result = book_service.create_book(book_data, db)
        if result == False:
            raise BookAlreadyExistsError()
        db.commit()
        return JSONResponse(status_code=201, content={"message": "Book registered successfully"})

    except BookAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=302, content={"message": "Book already exists"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        raise e
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "Book registration failed"})

    finally:
        db.close()


# 과목이 없는 경우 에러가 걸림

@router.get("/duplicate_book/{booktitle}")
async def duplicate_subject(request: Request, booktitle: str):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        found_book = book_service.find_book_by_title(booktitle, user_id, db)

        if found_book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})

        return JSONResponse(status_code=409, content={"message": f"Book '{booktitle}' already exists"})

    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})

    finally:
        db.close()


# @router.get("/book/{booktitle}")
# async def book_info(request: Request, booktitle: str):
#     db = get_db()
#     try:
#         userid = AuthorizationService.verify_session(request, db)

#         if (book := book_service.find_book_by_title(booktitle, userid, db)).userid != userid:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})

#         if book == None:
#             return JSONResponse(status_code=404, content={"message": "Book not found"})

#         return JSONResponse(status_code=200, content={"book": book_service.to_book_data(book).__dict__})

#     except SessionIdNotFoundError as e:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})

#     finally:
#         db.close()


@router.get("/book/{book_id}")#완벽
async def book_info(request: Request, book_id: str):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        book = book_service.find_book_by_id(book_id, db)
        if book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        if book.user_id != user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        user = user_service.find_user_by_id(book.user_id, db)
        subject = subject_service.find_subject_by_id(book.subject_id, db)
        user = user_service.to_user_data(user).__dict__
        subject = subject_service.to_subject_data(subject).__dict__
        book = book_service.to_book_data(book).__dict__
        book['user'] = user
        book['subject'] = subject
        del book['subject_id']
        del book['user_id']
        return JSONResponse(status_code=200, content={"message": book})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})

    finally:
        db.close()

    #사용자가 book에 대해서 검색할 엔드포인트가 존재해야 함.


# @router.get("/book/{subject}")  # 이거 이름 수정하고 과목에 대한 엔드포인트로 변경
# async def get_subject_book(request: Request, subject: str):
#     db = get_db()
#     try:
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         if (found_book := book_service.find_book_by_subject(subject, user_id, db)).user_id != user_id:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})

#         if found_book == None:
#             return JSONResponse(status_code=404, content={"message": "Book not found"})

#         data = [book_service.to_book_data(book).dict() for book in found_book]

#         return JSONResponse(status_code=200, content=data)

#     except SessionIdNotFoundError as e:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"message": "Subject retrieval failed"})

#     finally:
#         db.close()

# @router.get("/book/{subject_id}")  # 이거 이름 수정하고 과목에 대한 엔드포인트로 변경
# async def get_subject_book_by_id(request: Request, subject_id: str):
#     db = get_db()
#     try:
#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         if (found_book := book_service.find_book_by_subject_id(subject_id, user_id, db)).user_id != user_id:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        
#         if found_book == None:
#             return JSONResponse(status_code=404, content={"message": "Book not found"})

#         data = [book_service.to_book_data(book).dict() for book in found_book]

#         return JSONResponse(status_code=200, content=data)

#     except SessionIdNotFoundError as e:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"message": "Subject retrieval failed"})

#     finally:
#         db.close()


# @router.get("/book_subject/{booktitle}")
# async def book_subject_by_title(request: Request, booktitle: str):
#     db = get_db()
#     try:
#         userid = AuthorizationService.verify_session(request, db)

#         if book_service.find_book_by_title(booktitle, userid, db).userid != userid:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})

#         book = book_service.find_book_by_title(booktitle, userid, db)

#         if book == None:
#             return JSONResponse(status_code=404, content={"message": "Book not found"})

#         return JSONResponse(status_code=200, content={"subject": book_service.to_book_data(book).__dict__["subject"]})

#     except SessionIdNotFoundError as e:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})

#     finally:
#         db.close()


@router.get("/book_subject/{book_id}")
async def book_subject_by_id(request: Request, book_id: str):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        if (book := book_service.find_book_by_id(book_id, db)).user_id != user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})

        if book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})

        return JSONResponse(status_code=200, content={"message": book_service.to_book_data(book).__dict__["subject"]})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book"})

    finally:
        db.close()


# 통합 검색 기능
@router.get("/book_search/{keyword}")
async def book_search(request: Request, keyword: str):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        books = book_service.find_book_by_partial_title(keyword, user_id, db)

        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)

        books = book_service.find_book_by_initial(keyword, user_id, db)
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)

        books = book_service.find_book_by_subject(keyword, user_id, db)
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)

        unique_books = {}
        for book in book_list:
            unique_books[book['id']] = book

        book_list = list(unique_books.values())

        return JSONResponse(status_code=200, content={"message": book_list})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=400, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=400, content={"message": "Token verification failed"})

    except Exception as e:
        return JSONResponse(status_code=409, content={"message": "There was some error while checking the book list"})

    finally:
        db.close()


@router.get("/active_book_list")
async def active_book_list(request: Request):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        books = book_service.find_book_by_status(True, user_id, db)

        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)

        return JSONResponse(status_code=200, content={"message": book_list})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})

    finally:
        db.close()


@router.get("/inactive_book_list")
async def inactive_book_list(request: Request):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        books = book_service.find_book_by_status(False, user_id, db)

        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)

        return JSONResponse(status_code=200, content={"message": book_list})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})

    finally:
        db.close()


@router.get("/book_list")
async def book_list(request: Request):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        books = db.query(book).filter(book.user_id == user_id).all()

        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)

        return JSONResponse(status_code=200, content={"message": book_list})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})

    finally:
        db.close()


# @router.get("/book_list/{subject}")
# async def book_list_by_subject(request: Request, subject: str):
#     db = get_db()
#     try:
#         userid = AuthorizationService.verify_session(request, db)

#         books = book_service.find_book_by_subject(subject, userid, db)

#         book_list = []
#         for book_entity in books:
#             book_list.append(book_service.to_book_data(book_entity).__dict__)

#         return JSONResponse(status_code=200, content={"books": book_list})

#     except SessionIdNotFoundError as e:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})

#     finally:
#         db.close()

@router.get("/book_list/{subject_id}")#완료
async def book_list_by_subject(request: Request, subject_id: str):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        subject = subject_service.find_subject_by_id(subject_id, db)
        if subject.user_id != user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this subject's book"})
        books = book_service.find_book_by_subject_id(subject_id, db)
        data = {
            'subject': subject_service.to_subject_data(subject).__dict__,
        }
        book_list = []
        for book_entity in books:
            book = book_service.to_book_data(book_entity).__dict__
            del book['user_id']
            del book['subject_id']
            book_list.append(book)
        data['books'] = book_list

        #book_list = [book_service.to_book_data(book_entity).__dict__ for book_entity in books]

        return JSONResponse(status_code=200, content={"message": data})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        raise e 
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the book list"})

    finally:
        db.close()


# @router.post("/edit_book/{title}")
# async def edit_book_by_title(request: Request, book_data: book_edit, title: str):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))

#         userid = AuthorizationService.verify_session(request, db)

#         book = book_service.edit_book_by_title(book_data, userid, title, db)

#         if book == False:
#             return JSONResponse(status_code=302, content={"message": "Book title already exists"})

#         db.commit()

#         return JSONResponse(status_code=200, content={"message": "Book edited successfully"})

#     except SessionIdNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": e.__str__()})

#     finally:
#         db.close()

@router.post("/edit_book")
async def edit_book_by_id(request: Request, book_data: book_edit):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        book_id = book_data.id
        book = book_service.find_book_by_id(book_id, db)
        if book == None:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        if book.user_id != user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this subject's book"})
        book_service.edit_book_by_id(book_data, user_id, book_id, db)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    
    except DuplicateBookTitleError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=302, content={"message": "Book title already exists"})

    except Exception as e:
        raise e
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": e.__str__()})

    finally:
        db.close()

# @router.delete("/book_delete/{title}")
# async def book_delete_by_name(request: Request, title: str):
#     db = get_db()
#     try:
#         db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
#         db.execute(text("SAVEPOINT savepoint"))

#         session = AuthorizationService.verify_session(request, db)
#         user_id = session['id']
#         if book_service.find_book_by_title(title, user_id, db).user_id != user_id:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this book"})

#         book_service.delete_book_by_name(title, user_id, db)

#         db.commit()

#         return JSONResponse(status_code=200, content={"message": "Book deleted successfully"})

#     except SessionIdNotFoundError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         rollback_to_savepoint(db)
#         return JSONResponse(status_code=500, content={"message": "There was some error while deleting the book"})

#     finally:
#         db.close()


@router.delete("/book_delete/{book_id}")
async def book_delete_by_id(request: Request, book_id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))

        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        if book_service.find_book_by_id(book_id, db).user_id != user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this book"})
        book_service.delete_book_by_id(book_id, db)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Book deleted successfully"})

    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        raise e
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "There was some error while deleting the book"})

    finally:
        db.close()