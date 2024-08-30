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

@router.post("/book/register")
async def book_register(request: Request, book_data: book_register):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        book_data = book_service.to_book_db(book_data, requester_id)
        book_service.register_book(book_data, db)
        return JSONResponse(status_code=201, content={"message": "Book registered successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except EmptyTitleError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
    except NegativePageNumberError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Page number cannot be negative"})
    except PageRangeError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Start page cannot be greater than end page"})
    except SubjectNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Subject not found"})
    except BookAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book already exists"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=500, content={"message": "Book registration failed"})
    finally:
        db.close()

@router.get("/book/check_title_available")
async def check_title_available(request: Request, title: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        if book_service.is_title_exists(title, requester_id, db):
            raise BookAlreadyExistsError
        return JSONResponse(status_code=200, content={"message": "Title is available"})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except BookAlreadyExistsError as e:
        return JSONResponse(status_code=409, content={"message": "Book already exists"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Book check failed"})
    finally:
        db.close()

@router.get("/book/id/{id}")
async def get_book_by_id(request: Request, id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        user = user_service.find_user_by_id(found_book.user_id, db)
        if not user:
            raise UserNotFoundError
        user = user_service.to_user_data(user).__dict__
        subject = subject_service.find_subject_by_id(found_book.subject_id, db)
        if not subject:
            subject = None
        else:
            subject = subject_service.to_subject_data(subject).__dict__
            del subject['user_id']
        found_book = book_service.to_book_data(found_book).__dict__
        found_book['user'] = user
        found_book['subject'] = subject
        del found_book['subject_id']
        del found_book['user_id']
        return JSONResponse(status_code=200, content={"message": found_book})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
    except UserNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Book find failed"})
    finally:
        db.close()

#굳이 존재할 필요가 없을 듯
@router.get("/book/book_subject/{id}")
async def get_book_subject(request: Request, id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        book_subject = subject_service.find_subject_by_id(found_book.subject_id, db)
        if not book_subject:
            found_subject = None
        else:
            found_subject = subject_service.to_subject_data(book_subject).__dict__
            del found_subject['user_id']
        return JSONResponse(status_code=200, content={"message": found_subject})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Book find failed"})
    finally:
        db.close()

@router.get("/book/book_list")
async def get_book_list(request: Request):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        book_list = book_service.find_book_by_user_id(requester_id, db)
        if not book_list:
            raise BookNotFoundError
        found_book = []
        for book in book_list:
            user = user_service.find_user_by_id(book.user_id, db)
            if not user:
                raise UserNotFoundError
            user = user_service.to_user_data(user).__dict__
            subject = subject_service.find_subject_by_id(book.subject_id, db)
            if not subject:
                subject = None
            else:
                subject = subject_service.to_subject_data(subject).__dict__
                del subject['user_id']
            book = book_service.to_book_data(book).__dict__
            book['user'] = user
            book['subject'] = subject
            del book['subject_id']
            del book['user_id']
            found_book.append(book)
        return JSONResponse(status_code=200, content={"message": found_book})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UserNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Book find failed"})
    finally:
        db.close()

#과목을 기준으로 책을 전체 반환하는 라우터 코드 추가

#책은 활성화 비활성화 모두를 반환하지만 거기서 사용하는 몫은 프론트에게 전가
#예외는 활성화책 비활성화책 목록 반환하는 엔드포인트만 냅두면 됌

@router.get("/book/book_list/{subject_id}")
async def book_list_by_subject(request: Request, subject_id: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        book_subject = subject_service.find_subject_by_id(subject_id, db)
        if not book_subject:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, book_subject.user_id)
        found_book = book_service.find_book_by_subject_id(subject_id, db)
        user = user_service.find_user_by_id(book_subject.user_id, db)
        subject = subject_service.to_subject_data(book_subject).__dict__
        user = user_service.to_user_data(user).__dict__
        subject['user'] = user
        del subject['user_id']
        data = {
            'subject': subject,
        }
        book_list = []
        for book_entity in found_book:
            book = book_service.to_book_data(book_entity).__dict__
            del book['user_id']
            del book['subject_id']
            book_list.append(book)
        data['books'] = book_list
        return JSONResponse(status_code=200, content={"message": data})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        return JSONResponse(status_code=403, content={"message": "You are not authorized to view this book"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Book find failed"})
    finally:
        db.close()

@router.get("/book/book_list/status/{status}")
async def book_list_by_status(request: Request, status: bool):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        book_list = book_service.find_book_by_status(status, requester_id, db)
        found_book = []
        for book in book_list:
            user = user_service.find_user_by_id(book.user_id, db)
            if not user:
                raise UserNotFoundError
            user = user_service.to_user_data(user).__dict__
            subject = subject_service.find_subject_by_id(book.subject_id, db)
            if not subject:
                subject = None
            else:
                subject = subject_service.to_subject_data(subject).__dict__
                del subject['user_id']
            book = book_service.to_book_data(book).__dict__
            book['user'] = user
            book['subject'] = subject
            del book['subject_id']
            del book['user_id']
            found_book.append(book)
        return JSONResponse(status_code=200, content={"message": found_book})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        return JSONResponse(status_code=409, content={"message": "Book find failed"})
    finally:
        db.close()

# 통합 검색 기능
# 알고리즘 최적화
@router.get("/search/book/{keyword}")
async def book_search(request: Request, keyword: str):
    db = get_db()
    try:
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        book_list = []
        books = book_service.find_book_by_partial_title(keyword, requester_id, db)
        book_list = book_list + books
        books = book_service.find_book_by_initial(keyword, requester_id, db)
        book_list = book_list + books
        books = book_service.find_book_by_subject(keyword, requester_id, db)
        book_list = book_list + books
        found_book = []
        for book in book_list:
            user = user_service.find_user_by_id(book.user_id, db)
            if not user:
                raise UserNotFoundError
            user = user_service.to_user_data(user).__dict__
            subject = subject_service.find_subject_by_id(book.subject_id, db)
            if not subject:
                subject = None
            else:
                subject = subject_service.to_subject_data(subject).__dict__
                del subject['user_id']
            book = book_service.to_book_data(book).__dict__
            book['user'] = user
            book['subject'] = subject
            del book['subject_id']
            del book['user_id']
            found_book.append(book)
        unique_books = {}
        for book in found_book:
            unique_books[book['id']] = book
        found_book = list(unique_books.values())
        return JSONResponse(status_code=200, content={"message": found_book})
    except SessionIdNotFoundError as e:
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=409, content={"message": "Book find failed"})
    finally:
        db.close()

#전체 edit은 디자인 보고 채용 여부 결정
@router.post("/edit/book_title/{id}")
async def edit_title(request: Request, book_data: book_title, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        book_service.edit_title(book_data.title, id, requester_id, db)
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
    except EmptyTitleError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
    except BookAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book already exists"})
    except BookNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book edit failed"})
    finally:
        db.close()

@router.post("/edit/book_subject_id/{id}")
async def edit_subject_id(request: Request, book_data: book_subject_id, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        book_service.edit_subject_id(book_data.subject_id, id, db)
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
    except SubjectNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Subject not found"})
    except BookAlreadyExistsError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book already exists"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book edit failed"})
    finally:
        db.close()

@router.post("/edit/book_page/{id}")
async def edit_page(request: Request, book_data: book_page, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        book_service.edit_page(book_data.start_page, book_data.end_page, id, db)
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
    except NegativePageNumberError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Page number cannot be negative"})
    except PageRangeError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=400, content={"message": "Start page cannot be greater than end page"})
    except BookNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book edit failed"})
    finally:
        db.close()

@router.post("/edit/book_memo/{id}")
async def edit_memo(request: Request, book_data: book_memo, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        book_service.edit_memo(book_data.memo, id, db)
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
    except BookNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book edit failed"})
    finally:
        db.close()

@router.post("/edit/book_status/{id}")
async def edit_status(request: Request, book_data: book_status, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        book_service.edit_status(book_data.status, id, db)
        return JSONResponse(status_code=200, content={"message": "Book edited successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
    except BookNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book edit failed"})
    finally:
        db.close()

@router.delete("/delete/book/{id}")
async def delete_book(request: Request, id: str):
    db = get_db()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        db.execute(text("SAVEPOINT savepoint"))
        requester_id = AuthorizationService.verify_session(request, db)["id"]
        found_book = book_service.find_book_by_id(id, db)
        if not found_book:
            raise UnauthorizedError
        AuthorizationService.check_authorization(requester_id, found_book.user_id)
        result = book_service.delete_book_by_id(id, db)
        if not result:
            raise BookNotFoundError
        return JSONResponse(status_code=200, content={"message": "Book deleted successfully"})
    except SessionIdNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=401, content={"message": "Token not found"})
    except SessionVerificationError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=417, content={"message": "Token verification failed"})
    except SessionExpiredError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=440, content={"message": "Session expired"})
    except UnauthorizedError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this book"})
    except BookNotFoundError as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=404, content={"message": "Book not found"})
    except Exception as e:
        rollback_to_savepoint(db)
        return JSONResponse(status_code=409, content={"message": "Book delete failed"})
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
#             return JSONResponse(status_code=409, content={"message": "Book title already exists"})

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

# @router.get("/subject_book_list")
# async def subject_book_list(request: Request):
#     db = get_db()
#     try:
#         requester_id = AuthorizationService.verify_session(request, db)["id"]
#         subjects = subject_service.find_subject_by_user_id(requester_id, db)
#         subject_list = []
#         data = {}
#         for subject_entity in subjects:
#             subject = subject_service.to_subject_data(subject_entity).__dict__
#             del subject['user_id']
#             subject_list.append(subject)
#         books = book_service.find_book_by_status(True, requester_id, db)
#         book_list = []
#         for book_entity in books:
#             book = book_service.to_book_data(book_entity).__dict__
#             del book['user_id']
#             del book['subject_id']
#             book_list.append(book)
#         data['subjects'] = subject_list
#         data['books'] = book_list
#         return JSONResponse(status_code=200, content={"message": data})
#     except SessionIdNotFoundError as e:
#         return JSONResponse(status_code=401, content={"message": "Token not found"})
#     except SessionVerificationError as e:
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#     except SessionExpiredError as e:
#         return JSONResponse(status_code=440, content={"message": "Session expired"})
#     except Exception as e:
#         return JSONResponse(status_code=409, content={"message": "Book find failed"})
#     finally:
#         db.close()