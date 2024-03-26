from io import BytesIO
import aiohttp
from PIL import Image
from fastapi import UploadFile
from app.routers.api_v1.OCR.constants import JPEG_RESIZED, OCR_API, PNG_RESIZED
from app.routers.api_v1.OCR.exceptions import IMAGE_FORMAT_NOT_SUPPORTED, OCR_FAILED
from config import initial_config as config
from app.routers.api_v1.Service.exception import (
    IMAGE_SIZE_EXCEEDED,
)


async def image_to_text(file: UploadFile):
    if not is_valid_image(file):
        raise IMAGE_FORMAT_NOT_SUPPORTED

    if not file.size:
        raise IMAGE_FORMAT_NOT_SUPPORTED

    if file.size >= config.MAX_IMAGE_SIZE:
        raise IMAGE_SIZE_EXCEEDED

    original_image: Image.Image = Image.open(file.file)
    image_format: str | None = original_image.format
    if not image_format:
        raise IMAGE_FORMAT_NOT_SUPPORTED

    resized_image_buffer = resize_image(original_image, image_format)

    if not image_format:
        raise IMAGE_FORMAT_NOT_SUPPORTED
    headers = {
        "apikey": OCR_API,
    }

    data = aiohttp.FormData()
    data.add_field(
        "file",
        resized_image_buffer.getvalue(),
        content_type=f"image/{image_format.lower()}",
        filename="resized_image." + image_format.lower(),
    )

    data.add_field("language", "eng")
    data.add_field("isOverlayRequired", "true")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.ocr.space/Parse/Image", headers=headers, data=data
        ) as response:
            response_data = await response.json()
            if response.status != 200:
                raise OCR_FAILED

            elif "ErrorMessage" in response_data:
                raise IMAGE_SIZE_EXCEEDED

            if "ParsedResults" in response_data and response_data["ParsedResults"]:
                text = response_data["ParsedResults"][0]["ParsedText"]
                return text
    raise OCR_FAILED


def is_valid_image(image):
    # Check if the file is an image with a supported format
    return image.filename.endswith((".jpg", ".jpeg", ".png"))


def resize_image(image: Image.Image, image_format: str):
    new_image = image
    if image_format.lower() == "png":
        new_image = image.resize(PNG_RESIZED)

    else:
        new_image = image.resize(JPEG_RESIZED)

    resized_image_buffer = BytesIO()
    new_image.save(resized_image_buffer, format=image_format)

    return resized_image_buffer
