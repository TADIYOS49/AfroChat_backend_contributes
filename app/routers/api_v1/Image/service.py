import base64
from fastapi import HTTPException, UploadFile
from PIL import Image
from io import BytesIO
import aiohttp
import requests
from app.routers.api_v1.Image.constants import (
    GOOGLE_GEMINI_API,
    IMAGE_GENERATOR_API,
    MAX_IMAGE_SIZE,
)
from config import initial_config as config
from app.routers.api_v1.Service.exception import (
    IMAGE_SIZE_EXCEEDED,
)

from app.routers.api_v1.Image.exceptions import (
    IMAGE_CAPTIONING_FAILED,
    IMAGE_EDITING_FAILED,
    IMAGE_EDITING_MODEL_BUSY,
    IMAGE_FORMAT_NOT_SUPPORTED,
    NO_INTERENT_CONNECTION,
)


async def generate_caption_from_image(image: UploadFile):
    if not is_valid_image(image):
        raise IMAGE_FORMAT_NOT_SUPPORTED

    if not image.size:
        raise IMAGE_FORMAT_NOT_SUPPORTED

    if image.size >= config.MAX_IMAGE_SIZE:
        raise IMAGE_SIZE_EXCEEDED

    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"

    img = Image.open(BytesIO(await image.read()))
    img_bytes = ImageToBase64String(img)

    headers = {"Authorization": f"Bearer {IMAGE_GENERATOR_API}"}
    payload = {"image": img_bytes}

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json=payload) as response:
            caption_list = await response.json()

    if isinstance(caption_list, list) and len(caption_list) > 0:
        caption = caption_list[0]
    else:
        caption = "No caption available"

    return caption


# Helper function to convert an image to a base64-encoded string
def ImageToBase64String(img):
    buffered = BytesIO()
    img.save(buffered, format=img.format)
    img_bytes = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_bytes


def is_valid_image(image):
    # Check if the file is an image with a supported format
    return image.filename.endswith((".jpg", ".jpeg", ".png", ".jfif"))


async def generate_description_from_image(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to download the image"
                )

            image_bytes = await response.read()

    img = Image.open(BytesIO(image_bytes))
    img_bytes = ImageToBase64String(img)

    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "key": GOOGLE_GEMINI_API,
    }

    json_data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Examine the image meticulously and provide a thorough description of every discernible element ",
                    },
                    {"inlineData": {"mimeType": "image/jpeg", "data": img_bytes}},
                ],
            },
        ],
    }

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL, params=params, headers=headers, json=json_data
        ) as response:
            response_json = await response.json()

            if response.status == 200:
                return response_json["candidates"][0]["content"]["parts"][0]["text"]

            else:
                raise IMAGE_CAPTIONING_FAILED


async def edit_image_with_prompt(image_url: str, prompt: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to download the image"
                )

            image_bytes = await response.read()

    img = Image.open(BytesIO(image_bytes))
    img_bytes = ImageToBase64String(img)
    payload = {"inputs": img_bytes, "parameters": {"prompt": prompt}}

    headers = {"Authorization": f"Bearer {IMAGE_GENERATOR_API}"}
    API_URL = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                image_bytes = await response.read()
                return image_bytes
            elif response.status == 503:
                raise IMAGE_EDITING_MODEL_BUSY
            else:
                raise IMAGE_EDITING_FAILED

    await session.close()
