from fastapi import HTTPException, status


class BadRequestHTTPException(HTTPException):
    def __init__(self, msg: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg if msg else "Bad request",
        )


class UnprocessableEntityHTTPException(HTTPException):
    def __init__(self, msg: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=msg if msg else "Unprocessable Entity",
        )


class AuthFailedHTTPException(HTTPException):
    def __init__(self, msg: str | None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg if msg else "Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthTokenExpiredHTTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenHTTPException(HTTPException):
    def __init__(self, msg: str | None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg if msg else "Requested resource is forbidden",
        )


class NotFoundHTTPException(HTTPException):
    def __init__(self, msg: str | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg if msg else "Requested resource is not found",
        )


class ConflictHTTPException(HTTPException):
    def __init__(self, msg: str | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg if msg else "Conflicting resource request",
        )


class ServiceNotAvailableHTTPException(HTTPException):
    def __init__(self, msg: str | None = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=msg if msg else "Service not available",
        )


class TooManyRequestsException(HTTPException):
    def __init__(self, msg: str | None = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=msg if msg else "Too many requests",
        )


class UnAuthorizedResourceAccess(HTTPException):
    def __init__(self, msg: str | None = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg if msg else "UnAuthorized or No Access to Resource",
        )
