from fastapi import APIRouter, Depends, UploadFile
from app.routers.api_v1.Auth.dependencies import get_activated_user

from app.routers.api_v1.OCR.schemas import ParsedTextOut
from app.routers.api_v1.OCR.service import image_to_text


ocr_router = APIRouter(
    tags=["OCR"],
    responses={404: {"description": "Not found"}},
)


@ocr_router.post("/ocr", dependencies=[Depends(get_activated_user)])
async def ocr(
    file: UploadFile,
):
    return ParsedTextOut(text=await image_to_text(file))
