from app.exceptions import BadRequestHTTPException, NotFoundHTTPException

FULL_NAME_IS_REQUIRED = BadRequestHTTPException(msg="Full name is required")

CATEGORY_NOT_FOUND = NotFoundHTTPException(msg="Category not found")

FULL_NAME_NOT_FOUND = NotFoundHTTPException(msg="Full name not found")

PERSONA_NAME_ALREADY_EXISTS = BadRequestHTTPException(msg="Full name already exists")

PERSONA_NOT_FOUND = NotFoundHTTPException(msg="Persona not found")
