from fastapi import HTTPException, status
from app.exceptions import (
    UnprocessableEntityHTTPException,
    NotFoundHTTPException,
    UnAuthorizedResourceAccess,
)


# input field needs to have persona_id or tool_id

EMPTY_PERSONA_ID_AND_TOOL_ID = UnprocessableEntityHTTPException(
    msg="persona_id and tool_id cannot be None at the same time"
)

# only persona_id or tool_id can be filled

PERSONA_ID_AND_TOOL_ID_BOTH_FILLED = UnprocessableEntityHTTPException(
    msg="persona_id and tool_id cannot be filled at the same time"
)

# chat session not found

CHAT_SESSION_NOT_FOUND = NotFoundHTTPException(msg="chat session not found")

UNAUTHORIZED_RESOURCE_ACCESS = UnAuthorizedResourceAccess()

IMAGE_GENERATION_FAILED = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Image generation failed due to internal error",
)

MODEL_NOT_FOUND = UnprocessableEntityHTTPException(
    msg="Model selected not found, models available are model-a and model-b"
)

NO_INTERENT_CONNECTION = HTTPException(
    status_code=500, detail="Internal server error: No internet connection"
)

IMAGE_FORMAT_NOT_SUPPORTED = UnprocessableEntityHTTPException(
    msg="Image format not supported. Only .png, .jpg, .jpeg are supported"
)
