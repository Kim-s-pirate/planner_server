from fastapi.responses import JSONResponse
from sqlalchemy import text
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter
from starlette.status import *
from Service.authorization_service import *
import os
from dotenv import load_dotenv
from fastapi import Request
from Data.book import *
from Service.book_service import *
from collections import defaultdict

router = APIRouter(tags=["book"], prefix="/book")

@router.post("/register", summary="책 등록", description="책을 등록합니다.", responses={
    201: {"description": "성공", "content": {"application/json": {"example": {
    "id": "65d4701c9ab37db862c9d396c3020c9793d1110e73585c208987f89cacc67267",
    "user_id": "1b0725841ba6e6e4218e0a991bfaa6914dea00a041d98815724517ca846d8c27",
    "title": "test2",
    "start_page": 1,
    "end_page": 200,
    "memo": "",
    "status": True,
    "initial": "test2",
    "subject": {
        "id": "1a56983b7be69e6737b1cf59fc4fb2fbfa5930a9de8cffb06944818538f2d805",
        "user_id": "1b0725841ba6e6e4218e0a991bfaa6914dea00a041d98815724517ca846d8c27",
        "title": "science",
        "color": "#858585"
    }
}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    409: {"description": "중복된 제목", "content": {"application/json": {"example": {"message": "Book already exists"}}}},
    400: {"description": "페이지 번호 음수", "content": {"application/json": {"example": {"message": "Page number cannot be negative"}}}},
    400: {"description": "페이지 크기 문제", "content": {"application/json": {"example": {"message": "Start page cannot be greater than end page"}}}},
    400: {"description": "9999 페이지 초과", "content": {"application/json": {"example": {"message": "Page cannot exceed 9999 pages"}}}},
    500: {"description": "등록 실패", "content": {"application/json": {"example": {"message": "Book registration failed"}}}}
})
async def book_register(request: Request, book_data: book_register):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            book_data = book_service.to_book_db(book_data, requester_id)
            book = book_service.register_book(book_data, db)
            book = book_service.to_book_data(book).__dict__
            subject = subject_service.find_subject_by_id(book['subject_id'], db)
            subject = subject_service.to_subject_data(subject).__dict__
            del book['subject_id']
            book['subject'] = subject
            return JSONResponse(status_code=201, content=book)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except EmptyTitleError as e:
            return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
        except NegativePageNumberError as e:
            return JSONResponse(status_code=400, content={"message": "Page number cannot be negative"})
        except PageRangeError as e:
            return JSONResponse(status_code=400, content={"message": "Start page cannot be greater than end page"})
        except ExceedPageError as e:
            return JSONResponse(status_code=400, content={"message": "Page cannot exceed 9999 pages"})
        except SubjectNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Subject not found"})
        except BookAlreadyExistsError as e:
            return JSONResponse(status_code=409, content={"message": "Book already exists"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Book registration failed"})

@router.get("/check_title_available", summary="책 제목 중복 확인", description="책 제목이 중복되는지 확인합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Title is available"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    409: {"description": "중복된 제목", "content": {"application/json": {"example": {"message": "Book already exists"}}}},
    500: {"description": "중복 확인 실패", "content": {"application/json": {"example": {"message": "Book check failed"}}}}
})
async def check_title_available(request: Request, title: str):
    with get_db() as db:
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

@router.get("/id/{id}", summary="책 id 조회", description="책을 id를 통해서 조회합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": {"id": "1", "name": "Sample Book"}}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    403: {"description": "권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to view this book"}}}},
    404: {"description": "사용자 없음", "content": {"application/json": {"example": {"message": "User not found"}}}},
    500: {"description": "조회 실패", "content": {"application/json": {"example": {"message": "Book find failed"}}}}
})
async def get_book_by_id(request: Request, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_book = book_service.find_book_by_id(id, db)
            if not found_book:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_book.user_id)
            subject = subject_service.find_subject_by_id(found_book.subject_id, db)
            if not subject:
                subject = None
            else:
                subject = subject_service.to_subject_data(subject).__dict__
                del subject['user_id']
            found_book = book_service.to_book_data(found_book).__dict__
            del found_book['subject_id']
            found_book['subject'] = subject
            return JSONResponse(status_code=200, content=found_book)
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

@router.get("/list", summary="책 목록 조회", description="책 목록을 조회합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": [{"id": "1", "name": "Sample Book"}]}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    404: {"description": "사용자 없음", "content": {"application/json": {"example": {"message": "User not found"}}}},
    500: {"description": "목록 조회 실패", "content": {"application/json": {"example": {"message": "Book find failed"}}}}
})
async def get_book_list(request: Request):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            book_list = book_service.find_book_by_user_id(requester_id, db)
            if not book_list:
                raise BookNotFoundError
            found_book = []
            for book in book_list:
                subject = subject_service.find_subject_by_id(book.subject_id, db)
                if not subject:
                    subject = None
                else:
                    subject = subject_service.to_subject_data(subject).__dict__
                    del subject['user_id']
                book = book_service.to_book_data(book).__dict__
                book['subject'] = subject
                del book['subject_id']
                del book['user_id']
                found_book.append(book)
            result = {"user_id": requester_id, "book_list": found_book}
            return JSONResponse(status_code=200, content=result)
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

@router.get("/list_by_subject", summary="과목별 책 목록 조회", description="과목별로 나누어 책 목록을 조회합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": []}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    404: {"description": "사용자 없음", "content": {"application/json": {"example": {"message": "User not found"}}}},
    500: {"description": "조회 실패", "content": {"application/json": {"example": {"message": "Book find failed"}}}}
})
async def get_book_list_by_subject(request: Request):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            book_list = book_service.find_book_by_user_id(requester_id, db)
            if not book_list:
                raise BookNotFoundError
            grouped_books = defaultdict(list)
            for book in book_list:
                subject = subject_service.find_subject_by_id(book.subject_id, db)
                if not subject:
                    subject = None
                else:
                    subject = subject_service.to_subject_data(subject).__dict__
                    del subject['user_id']
                book = book_service.to_book_data(book).__dict__
                del book['subject_id']
                del book['user_id']
                grouped_books[subject['id']].append(book)
            result = []
            for subject_id, books in grouped_books.items():
                subject_info = subject_service.find_subject_by_id(subject_id, db)
                if subject_info:
                    subject_info = subject_service.to_subject_data(subject_info).__dict__
                    del subject_info['user_id']
                    subject_info['books'] = books
                    result.append(subject_info)
            result = {"user_id": requester_id, "list": result}
            return JSONResponse(status_code=200, content=result)
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

#책은 활성화 비활성화 모두를 반환하지만 거기서 사용하는 몫은 프론트에게 전가
#예외는 활성화책 비활성화책 목록 반환하는 엔드포인트만 냅두면 됌

@router.get("/list/{subject_id}", summary="과목 책 조회", description="해당 과목에 속하는 책 목록을 조회합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": {"subject": {}, "books": []}}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    403: {"description": "권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to view this book"}}}},
    404: {"description": "사용자 없음", "content": {"application/json": {"example": {"message": "User not found"}}}},
    500: {"description": "조회 실패", "content": {"application/json": {"example": {"message": "Book find failed"}}}}
})
async def book_list_by_subject(request: Request, subject_id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            book_subject = subject_service.find_subject_by_id(subject_id, db)
            if not book_subject:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, book_subject.user_id)
            found_book = book_service.find_book_by_subject_id(subject_id, db)
            subject = subject_service.to_subject_data(book_subject).__dict__
            del subject['user_id']
            result = {
                "user_id": requester_id,
                "subject": subject,
            }
            book_list = []
            for book_entity in found_book:
                book = book_service.to_book_data(book_entity).__dict__
                del book['user_id']
                del book['subject_id']
                book_list.append(book)
            result['books'] = book_list
            return JSONResponse(status_code=200, content=result)
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

@router.get("/list/status/{status}", summary="책 상태별 조회", description="활성화/비활성화(active/inactive)된 책 목록을 조회합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": []}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    404: {"description": "유효하지 않은 status", "content": {"application/json": {"example": {"message": "Invalid Status"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    409: {"description": "조회 실패", "content": {"application/json": {"example": {"message": "Book find failed"}}}}
})
async def book_list_by_status(request: Request, status: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            if status == "active":
                status = True
            elif status == "inactive":
                status = False
            else:
                raise InvalidStatusError
            book_list = book_service.find_book_by_status(status, requester_id, db)
            found_book = []
            for book in book_list:
                subject = subject_service.find_subject_by_id(book.subject_id, db)
                if not subject:
                    subject = None
                else:
                    subject = subject_service.to_subject_data(subject).__dict__
                    del subject['user_id']
                book = book_service.to_book_data(book).__dict__
                book['subject'] = subject
                del book['subject_id']
                del book['user_id']
                found_book.append(book)
            result = {"user_id": requester_id, "book_list": found_book}
            return JSONResponse(status_code=200, content=result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except InvalidStatusError as e:
            return JSONResponse(status_code=404, content={"message": "Invalid Status"})
        except Exception as e:
            return JSONResponse(status_code=409, content={"message": "Book find failed"})

# 통합 검색 기능
# 알고리즘 최적화
# @router.get("/search/{keyword}", summary="책 검색", description="키워드로 책을 검색합니다.", responses={
#     200: {"description": "성공", "content": {"application/json": {"example": {"message": []}}}},
#     401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
#     417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
#     440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
#     409: {"description": "조회 실패", "content": {"application/json": {"example": {"message": "Book find failed"}}}}
# })
# async def book_search(request: Request, keyword: str):
#     with get_db() as db:
#         try:
#             requester_id = AuthorizationService.verify_session(request, db)["id"]
#             book_list = []
#             books = book_service.find_book_by_partial_title(keyword, requester_id, db)
#             book_list = book_list + books
#             books = book_service.find_book_by_initial(keyword, requester_id, db)
#             book_list = book_list + books
#             books = book_service.find_book_by_subject(keyword, requester_id, db)
#             book_list = book_list + books
#             found_book = []
#             for book in book_list:
#                 subject = subject_service.find_subject_by_id(book.subject_id, db)
#                 if not subject:
#                     subject = None
#                 else:
#                     subject = subject_service.to_subject_data(subject).__dict__
#                     del subject['user_id']
#                 book = book_service.to_book_data(book).__dict__
#                 book['subject'] = subject
#                 del book['subject_id']
#                 del book['user_id']
#                 found_book.append(book)
#             unique_books = {}
#             for book in found_book:
#                 unique_books[book['id']] = book
#             found_book = list(unique_books.values())
#             result = {"user_id": requester_id, "book_list": found_book}
#             return JSONResponse(status_code=200, content = result)
#         except SessionIdNotFoundError as e:
#             return JSONResponse(status_code=401, content={"message": "Token not found"})
#         except SessionVerificationError as e:
#             return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#         except SessionExpiredError as e:
#             return JSONResponse(status_code=440, content={"message": "Session expired"})
#         except Exception as e:
#             print(e)
#             return JSONResponse(status_code=409, content={"message": "Book find failed"})

#전체 edit은 디자인 보고 채용 여부 결정
@router.post("/edit/title/{id}", summary="책 제목 수정", description="책 제목을 수정합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Book edited successfully"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    403: {"description": "수정 권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to edit this book"}}}},
    409: {"description": "수정 실패", "content": {"application/json": {"example": {"message": "Book edit failed"}}}}
})
async def edit_title(request: Request, book_data: book_title, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_book = book_service.find_book_by_id(id, db)
            if not found_book:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_book.user_id)
            book = book_service.edit_title(book_data.title, id, requester_id, db)
            book = book_service.to_book_data(book).__dict__
            subject = subject_service.find_subject_by_id(book['subject_id'], db)
            subject = subject_service.to_subject_data(subject).__dict__
            book['subject'] = subject
            del book['subject_id']
            result = {"user_id": requester_id, "book": book}
            return JSONResponse(status_code=200, content= result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
        except EmptyTitleError as e:
            return JSONResponse(status_code=409, content={"message": "Title cannot be blank"})
        except BookAlreadyExistsError as e:
            return JSONResponse(status_code=409, content={"message": "Book already exists"})
        except BookNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        except Exception as e:
            return JSONResponse(status_code=409, content={"message": "Book edit failed"})

# @router.post("/edit/subject/{id}", summary="책 과목 수정", description="책 과목을 수정합니다.", responses={
#     200: {"description": "성공", "content": {"application/json": {"example": {"message": "Book edited successfully"}}}},
#     401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
#     417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
#     440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
#     403: {"description": "수정 권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to edit this book"}}}},
#     404: {"description": "과목 없음", "content": {"application/json": {"example": {"message": "Subject not found"}}}},
#     409: {"description": "수정 실패", "content": {"application/json": {"example": {"message": "Book edit failed"}}}}
# })
# async def edit_subject_id(request: Request, book_data: book_subject_id, id: str):
#     with get_db() as db:
#         try:
#             requester_id = AuthorizationService.verify_session(request, db)["id"]
#             found_book = book_service.find_book_by_id(id, db)
#             if not found_book:
#                 raise UnauthorizedError
#             AuthorizationService.check_authorization(requester_id, found_book.user_id)
#             book = book_service.edit_subject_id(book_data.subject_id, id, db)
#             book = book_service.to_book_data(book).__dict__
#             subject = subject_service.find_subject_by_id(book['subject_id'], db)
#             subject = subject_service.to_subject_data(subject).__dict__
#             del subject['user_id']
#             book['subject'] = subject
#             del book['subject_id']
#             del book['user_id']
#             result = {"user_id": requester_id, "book": book}
#             return JSONResponse(status_code=200, content=result)
#         except SessionIdNotFoundError as e:
#             return JSONResponse(status_code=401, content={"message": "Token not found"})
#         except SessionVerificationError as e:
#             return JSONResponse(status_code=417, content={"message": "Token verification failed"})
#         except SessionExpiredError as e:
#             return JSONResponse(status_code=440, content={"message": "Session expired"})
#         except UnauthorizedError as e:
#             return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
#         except SubjectNotFoundError as e:
#             return JSONResponse(status_code=404, content={"message": "Subject not found"})
#         except BookAlreadyExistsError as e:
#             return JSONResponse(status_code=409, content={"message": "Book already exists"})
#         except Exception as e:
#             return JSONResponse(status_code=409, content={"message": "Book edit failed"})

@router.post("/edit/page/{id}", summary="책 페이지 수정", description="책 페이지를 수정합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Book edited successfully"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    403: {"description": "수정 권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to edit this book"}}}},
    400: {"description": "페이지 번호 음수", "content": {"application/json": {"example": {"message": "Page number cannot be negative"}}}},
    400: {"description": "페이지 크기 문제", "content": {"application/json": {"example": {"message": "Start page cannot be greater than end page"}}}},
    400: {"description": "9999 페이지 초과", "content": {"application/json": {"example": {"message": "Page cannot exceed 9999 pages"}}}},
    404: {"description": "책 없음", "content": {"application/json": {"example": {"message": "Book not found"}}}},
    409: {"description": "수정 실패", "content": {"application/json": {"example": {"message": "Book edit failed"}}}}
})
async def edit_page(request: Request, book_data: book_page, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_book = book_service.find_book_by_id(id, db)
            if not found_book:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_book.user_id)
            book = book_service.edit_page(book_data.start_page, book_data.end_page, id, db)
            book = book_service.to_book_data(book).__dict__
            subject = subject_service.find_subject_by_id(book['subject_id'], db)
            subject = subject_service.to_subject_data(subject).__dict__
            del subject['user_id']
            book['subject'] = subject
            del book['subject_id']
            del book['user_id']
            result = {"user_id": requester_id, "book": book}
            return JSONResponse(status_code=200, content=result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
        except NegativePageNumberError as e:
            return JSONResponse(status_code=400, content={"message": "Page number cannot be negative"})
        except PageRangeError as e:
            return JSONResponse(status_code=400, content={"message": "Start page cannot be greater than end page"})
        except ExceedPageError as e:
            return JSONResponse(status_code=400, content={"message": "Page cannot exceed 9999 pages"})
        except BookNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        except Exception as e:
            return JSONResponse(status_code=409, content={"message": "Book edit failed"})

@router.post("/edit/memo/{id}", summary="책 메모 수정", description="책 메모를 수정합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Book edited successfully"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    403: {"description": "수정 권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to edit this book"}}}},
    404: {"description": "책 없음", "content": {"application/json": {"example": {"message": "Book not found"}}}},
    409: {"description": "수정 실패", "content": {"application/json": {"example": {"message": "Book edit failed"}}}}
})
async def edit_memo(request: Request, book_data: book_memo, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_book = book_service.find_book_by_id(id, db)
            if not found_book:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_book.user_id)
            book = book_service.edit_memo(book_data.memo, id, db)
            book = book_service.to_book_data(book).__dict__
            subject = subject_service.find_subject_by_id(book['subject_id'], db)
            subject = subject_service.to_subject_data(subject).__dict__
            del subject['user_id']
            book['subject'] = subject
            del book['subject_id']
            del book['user_id']
            result = {"user_id": requester_id, "book": book}
            return JSONResponse(status_code=200, content=result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
        except BookNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        except Exception as e:
            return JSONResponse(status_code=409, content={"message": "Book edit failed"})

@router.post("/edit/status/{id}", summary="책 상태 수정", description="책 상태를 수정합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Book edited successfully"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    403: {"description": "수정 권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to edit this book"}}}},
    404: {"description": "책 없음", "content": {"application/json": {"example": {"message": "Book not found"}}}},
    409: {"description": "수정 실패", "content": {"application/json": {"example": {"message": "Book edit failed"}}}}
})
async def edit_status(request: Request, book_data: book_status, id: str):
    with get_db() as db:
        try:
            requester_id = AuthorizationService.verify_session(request, db)["id"]
            found_book = book_service.find_book_by_id(id, db)
            if not found_book:
                raise UnauthorizedError
            AuthorizationService.check_authorization(requester_id, found_book.user_id)
            book = book_service.edit_status(book_data.status, id, db)
            book = book_service.to_book_data(book).__dict__
            subject = subject_service.find_subject_by_id(book['subject_id'], db)
            subject = subject_service.to_subject_data(subject).__dict__
            del subject['user_id']
            book['subject'] = subject
            del book['subject_id']
            del book['user_id']
            result = {"user_id": requester_id, "book": book}
            return JSONResponse(status_code=200, content=result)
        except SessionIdNotFoundError as e:
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to edit this book"})
        except BookNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        except Exception as e:
            return JSONResponse(status_code=409, content={"message": "Book edit failed"})

@router.delete("/delete/{id}", summary="책 id 삭제", description="책을 id로 삭제합니다.", responses={
    200: {"description": "성공", "content": {"application/json": {"example": {"message": "Book deleted successfully"}}}},
    401: {"description": "토큰이 없음", "content": {"application/json": {"example": {"message": "Token not found"}}}},
    417: {"description": "토큰 검증 실패", "content": {"application/json": {"example": {"message": "Token verification failed"}}}},
    440: {"description": "세션 만료", "content": {"application/json": {"example": {"message": "Session expired"}}}},
    403: {"description": "삭제 권한 없음", "content": {"application/json": {"example": {"message": "You are not authorized to delete this book"}}}},
    404: {"description": "책 없음", "content": {"application/json": {"example": {"message": "Book not found"}}}},
    409: {"description": "삭제 실패", "content": {"application/json": {"example": {"message": "Book delete failed"}}}}
})
async def delete_book(request: Request, id: str):
    with get_db() as db:
        try:
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
            return JSONResponse(status_code=401, content={"message": "Token not found"})
        except SessionVerificationError as e:
            return JSONResponse(status_code=417, content={"message": "Token verification failed"})
        except SessionExpiredError as e:
            return JSONResponse(status_code=440, content={"message": "Session expired"})
        except UnauthorizedError as e:
            return JSONResponse(status_code=403, content={"message": "You are not authorized to delete this book"})
        except BookNotFoundError as e:
            return JSONResponse(status_code=404, content={"message": "Book not found"})
        except Exception as e:
            return JSONResponse(status_code=409, content={"message": "Book delete failed"})




























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
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         
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
#         
#         return JSONResponse(status_code=401, content={"message": "Token not found"})

#     except SessionVerificationError as e:
#         
#         return JSONResponse(status_code=417, content={"message": "Token verification failed"})

#     except Exception as e:
#         
#         return JSONResponse(status_code=500, content={"message": "There was some error while deleting the book"})

#     finally:
#         db.close()

# 에러 수정해서 넣기
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
