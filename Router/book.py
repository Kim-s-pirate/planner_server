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

@router.post("/register/book")
async def register_book(request: Request, book_data: book_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        book_data = book_service.to_book_db(book_data, requester_id)
        book_service.create_book(book_data, db)
        return JSONResponse(status_code=201, content={"message": "Book registered successfully"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookAlreadyExistsError:
        return JSONResponse(status_code=302, content={"message": "Book already exists"})
    except:
        return JSONResponse(status_code=500, content={"message": "Book registration failed"})
    finally:
        db.close()

@router.get("/book/check_title_exists")
async def duplicate_subject(request: Request, title: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        book_service.check_title_exists(title, requester_id, db)
        return JSONResponse(status_code=200, content={"message": "Title is available"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookAlreadyExistsError:
        return JSONResponse(status_code=302, content={"message": "Book already exists"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the subject"})
    finally:
        db.close()


@router.get("/book/{id}")
async def get_book_by_id(request: Request, id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if requester_id != found_book.user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        ###############
        user = user_service.find_user_by_id(book.user_id, db)
        subject = subject_service.find_subject_by_id(book.subject_id, db)
        user = user_service.to_user_data(user).__dict__
        subject = subject_service.to_subject_data(subject).__dict__
        found_book = book_service.to_book_data(found_book).__dict__
        found_book['user'] = user
        found_book['subject'] = subject
        del found_book['subject_id']
        del found_book['user_id']
        return JSONResponse(status_code=200, content={"message": found_book})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the book"})
    finally:
        db.close()

@router.get("/book/book_subject/{id}")
async def get_book_subject(request: Request, id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if requester_id != found_book.user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        return JSONResponse(status_code=200, content={"message": found_book})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the book"})
    finally:
        db.close()

# book_list 쿼리 파라미터로 통합 필요
@router.get("/book/book_list")
async def book_list(request: Request):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)
        books = book_service.find_book_by_user_id(requester_id, db)
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"message": book_list})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the book list"})
    finally:
        db.close()

@router.get("/book/book_list/{subject_id}")
async def book_list_by_subject(request: Request, subject_id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)
        subject = subject_service.find_subject_by_id(subject_id, db)
        if requester_id != subject.user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book list"})
        ####################
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
        return JSONResponse(status_code=200, content={"message": data})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except:
        return JSONResponse(status_code=500, content={"message": "There was some error while viewing the book list"})
    finally:
        db.close()

@router.get("/book/book_list/status/{status}")
async def book_list_by_status(request: Request, status: bool):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)
        books = book_service.find_book_by_status(status, requester_id, db)
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        return JSONResponse(status_code=200, content={"message": book_list})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=409, content={"message": "There was some error while viewing the book list"})
    finally:
        db.close()

# 통합 검색 기능
@router.get("/search/book/{keyword}")
async def book_search(request: Request, keyword: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)
        books = book_service.find_book_by_partial_title(keyword, requester_id, db)
        book_list = []
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        books = book_service.find_book_by_initial(keyword, requester_id, db)
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        books = book_service.find_book_by_subject(keyword, requester_id, db)
        for book_entity in books:
            book_list.append(book_service.to_book_data(book_entity).__dict__)
        unique_books = {}
        for book in book_list:
            unique_books[book['id']] = book
        book_list = list(unique_books.values())
        return JSONResponse(status_code=200, content={"message": book_list})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except:
        return JSONResponse(status_code=409, content={"message": "There was some error while searching the book list"})
    finally:
        db.close()

@router.post("/edit/book/{id}")
async def edit_book_by_id(request: Request, book_data: book_edit, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if requester_id != found_book.user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
        book_service.edit_book(book_data, id, requester_id, db)
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except BookAlreadyExistsError:
        return JSONResponse(status_code=302, content={"message": "Book already exists"})
    except SubjectNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except NegativePageNumberError:
        return JSONResponse(status_code=400, content={"message": "Page number cannot be negative"})
    except PageRangeError:
        return JSONResponse(status_code=400, content={"message": "Start page cannot be greater than end page"})
    except:
        return JSONResponse(status_code=409, content={"message": "There was some error while editing the book"})
    finally:
        db.close()

@router.delete("/delete/book/{id}")
async def book_delete_by_id(request: Request, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        if requester_id != book_service.find_book_by_id(id, db).user_id:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this book"})
        book_service.delete_book_by_id(id, db)
        return JSONResponse(status_code=200, content={"message": "Book deleted successfully"})
    except SessionIdNotFoundError:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except:
        return JSONResponse(status_code=409, content={"message": "There was some error while deleting the book"})
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

@router.get("/subject_book_list")
async def subject_book_list(request: Request):
    db = get_db()
    try:
        session = AuthorizationService.verify_session(request, db)
        user_id = session['id']
        subjects = subject_service.find_subject_by_user_id(user_id, db)
        subject_list = []
        data = {}
        for subject_entity in subjects:
            subject = subject_service.to_subject_data(subject_entity).__dict__
            del subject['user_id']
            subject_list.append(subject)
        books = book_service.find_book_by_status(True, user_id, db)
        book_list = []
        for book_entity in books:
            book = book_service.to_book_data(book_entity).__dict__
            del book['user_id']
            del book['subject_id']
            book_list.append(book)
        data['subjects'] = subject_list
        data['books'] = book_list

        return JSONResponse(status_code=200, content={"message": data})

    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})

    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "There was some error while checking the subject list"})

    finally:
        db.close()
