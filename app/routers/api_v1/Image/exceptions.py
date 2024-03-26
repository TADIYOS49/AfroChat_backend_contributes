from fastapi import HTTPException, status
from app.exceptions import UnprocessableEntityHTTPException

IMAGE_GENERATION_FAILED = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Image generation failed due to internal error",
)

IMAGE_EDITING_FAILED = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Image editing failed due to internal error",
)

IMAGE_EDITING_MODEL_BUSY = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Image model is currently very busy",
)

IMAGE_CAPTIONING_FAILED = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Image captioning failed due to internal error",
)

MODEL_NOT_FOUND = UnprocessableEntityHTTPException(
    msg="Model selected not found, models available are model-a and model-b"
)

NO_INTERENT_CONNECTION = HTTPException(
    status_code=500, detail="Internal server error: No internet connection"
)


IMAGE_FORMAT_NOT_SUPPORTED = UnprocessableEntityHTTPException(
    msg="Image format not supported. Only .png, .jpg, .jpeg .jfif are supported"
)
