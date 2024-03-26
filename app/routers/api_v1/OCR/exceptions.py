from fastapi import HTTPException, status

from app.exceptions import UnprocessableEntityHTTPException


OCR_FAILED = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="OCR failed due to internal error",
)


IMAGE_FORMAT_NOT_SUPPORTED = UnprocessableEntityHTTPException(
    msg="Image format not supported. Only .png, .jpg, .jpeg are supported"
)
