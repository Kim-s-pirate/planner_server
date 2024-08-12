class UnauthorizedError(Exception):
    def __init__(self, message="You are not authorized to edit this user"):
        self.message = message
        super().__init__(self.message)

# user
class UserNotFoundError(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)

class UserAlreadyExistsError(Exception):
    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(self.message)

class InvalidUserDataError(Exception):
    def __init__(self, message="Invalid user data"):
        self.message = message
        super().__init__(self.message)

class UserUpdateError(Exception):
    def __init__(self, message="Failed to update user"):
        self.message = message
        super().__init__(self.message)

class DuplicateLoginError(Exception):
    def __init__(self, message="Duplicate login attempt detected"):
        self.message = message
        super().__init__(self.message)

# subject
class SubjectNotFoundError(Exception):
    def __init__(self, message="Subject not found"):
        self.message = message
        super().__init__(self.message)

class SubjectAlreadyExistsError(Exception):
    def __init__(self, message="Subject already exists"):
        self.message = message
        super().__init__(self.message)

class InvalidSubjectDataError(Exception):
    def __init__(self, message="Invalid subject data"):
        self.message = message
        super().__init__(self.message)

class SubjectUpdateError(Exception):
    def __init__(self, message="Failed to update subject"):
        self.message = message
        super().__init__(self.message)

class ColorExhaustedError(Exception):
    def __init__(self, message="No more colors available in the COLOR_SET"):
        self.message = message
        super().__init__(self.message)

# book        
class BookNotFoundError(Exception):
    def __init__(self, message="Book not found"):
        self.message = message
        super().__init__(self.message)

class BookAlreadyExistsError(Exception):
    def __init__(self, message="Book already exists"):
        self.message = message
        super().__init__(self.message)

class InvalidBookDataError(Exception):
    def __init__(self, message="Invalid book data"):
        self.message = message
        super().__init__(self.message)

class BookUpdateError(Exception):
    def __init__(self, message="Failed to update book"):
        self.message = message
        super().__init__(self.message)

class PageRangeError(Exception):
    def __init__(self, message="Start page cannot be greater than end page"):
        self.message = message
        super().__init__(self.message)

class NegativePageNumberError(Exception):
    def __init__(self, message="Page number cannot be negative"):
        self.message = message
        super().__init__(self.message)

#calendar
class ScheduleNotFoundError(Exception):
    def __init__(self, message="Schedule not found"):
        self.message = message
        super().__init__(self.message)

class InvalidScheduleDataError(Exception):
    def __init__(self, message="Invalid schedule data"):
        self.message = message
        super().__init__(self.message)

#planner
class BookSubjectMismatchError(Exception):
    def __init__(self, message="The subject of the book and the subject of the to-do do not match"):
        self.message = message
        super().__init__(self.message)

class TimeTableOverlapError(Exception):
    def __init__(self, message="The time table is overlapping"):
        self.message = message
        super().__init__(self.message)

#authorization
class SessionIdNotFoundError(Exception):
    def __init__(self):
        self.message = "Session ID not found"
        super().__init__(self.message)

class SessionVerificationError(Exception):
    def __init__(self):
        self.message = "Session verification failed"
        super().__init__(self.message)

class SessionExpiredError(Exception):
    def __init__(self):
        self.message = "Session expired"
        super().__init__(self.message)


class DatabaseCommitError(Exception):
    def __init__(self, message="Failed to commit to database"):
        self.message = message
        super().__init__(self.message)