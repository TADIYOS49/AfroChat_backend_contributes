from app.exceptions import ForbiddenHTTPException, NotFoundHTTPException


USER_NOT_OWNER_OF_SESSION = ForbiddenHTTPException(
    msg="User not the owner of the session"
)
SESSION_NOT_FOUND = NotFoundHTTPException(msg="session not found")
