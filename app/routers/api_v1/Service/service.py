from config import initial_config as config
import aiohttp

import cloudinary
import cloudinary.uploader

from fastapi import UploadFile, HTTPException

from app.routers.api_v1.Service.schemas import ImageUploadOut

cloudinary.config(
    cloud_name=config.CLOUDINARY_CLOUD_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
)


async def upload_image_to_cloudinary(file: UploadFile):
    upload_result = cloudinary.uploader.upload(file.file)

    return ImageUploadOut(
        secure_url=upload_result["secure_url"], public_id=upload_result["public_id"]
    )


async def transcribe_audio_whisper(audioFile: UploadFile):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        # "Content-Type": "multipart/form-data",  # Set the Content-Type header explicitly
    }

    data = aiohttp.FormData()
    data.add_field("file", audioFile.file.read(), content_type=audioFile.content_type)
    data.add_field("model", "whisper-1")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            response_data = await response.json()

            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail=response_data.get("error")
                )

            return response_data["text"]
