from fastapi import HTTPException, status
from app.exceptions import NotFoundHTTPException

RECIPIENT_NOT_FOUND = NotFoundHTTPException(msg="Recipient not found")

CHAT_SESSION_NOT_FOUND = NotFoundHTTPException(msg="Chat session not found")

MESSAGE_SHARING_FAILED = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Message Sharing Failed",
)
