from app.routers.api_v1.Service.constants import MAX_AUDIO_SIZE
from config import initial_config as config

from fastapi import APIRouter, Depends, UploadFile

from app.routers.api_v1.Service.schemas import ImageUploadOut, TranscribeOut

from app.routers.api_v1.Auth.dependencies import (
    is_admin_user,
)
from app.routers.api_v1.Service.exception import (
    IMAGE_SIZE_EXCEEDED,
    IMAGE_FORMAT_NOT_SUPPORTED,
)


from app.routers.api_v1.Service.exception import (
    AUDIO_SIZE_EXCEEDED,
    AUDIO_FORMAT_NOT_SUPPORTED,
)

from app.routers.api_v1.Service.service import (
    transcribe_audio_whisper,
    upload_image_to_cloudinary,
)

service_router = APIRouter(
    prefix="/service",
    tags=["Service"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        201: {"description": "Success"},
    },
)


@service_router.post(
    "/upload_image",
    status_code=201,
    response_model=ImageUploadOut,
    dependencies=[Depends(is_admin_user)],
)
async def upload_image(image: UploadFile):
    if not image.size:
        raise IMAGE_FORMAT_NOT_SUPPORTED
    if image.size > config.MAX_IMAGE_SIZE:
        raise IMAGE_SIZE_EXCEEDED

    # check image format
    if image.content_type not in [
        "image/png",
        "image/svg+xml",
        "image/jpeg",
        "image/jpg",
    ]:
        raise IMAGE_FORMAT_NOT_SUPPORTED

    return await upload_image_to_cloudinary(image)


@service_router.post(
    "/transcribe_audio",
    status_code=201,
    response_model=TranscribeOut,
)
async def transcribe_audio(audioFile: UploadFile):
    if audioFile.size > MAX_AUDIO_SIZE:
        raise AUDIO_SIZE_EXCEEDED

    # check image format
    if audioFile.content_type not in [
        "audio/flac",
        "audio/mp3",
        "audio/mp4",
        "audio/mpeg",
        "audio/mpga",
        "audio/m4a",
        "audio/ogg",
        "audio/wav",
        "audio/webm",
    ]:
        raise AUDIO_FORMAT_NOT_SUPPORTED

    return TranscribeOut(text=await transcribe_audio_whisper(audioFile))
