from app.exceptions import BadRequestHTTPException

VERSION_NAME_ALREADY_EXISTS = BadRequestHTTPException(msg="Version name already exists")
