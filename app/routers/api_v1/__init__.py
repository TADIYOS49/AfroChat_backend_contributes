from fastapi import APIRouter

from .Auth.router import auth_router
from .User.router import admin_crud_router
from .Persona.router import persona_router
from .Tools.router import tool_router
from .Tools.router import tool_router
from .chat.router import chat_router
from .Service.router import service_router
from .OCR.router import ocr_router
from .Share.router import share_router
from .Image.router import image_router
from .Overview.router import overview_router
from .PersonaStat.router import persona_stat_router
from .SubToolStat.router import sub_tool_stat_router
from .ToolStat.router import tool_stat_router
from .UserStat.router import user_stat_router
from .ExtraStat.router import extra_stat_router
from .Payment.router import payment_router
from .VersionControl.router import version_control_router
from .Explore.router import explore_router
from .Ask.router import ask_router

api_v1_router = APIRouter(prefix="/api_v1")

api_v1_router.include_router(chat_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(persona_router)
api_v1_router.include_router(tool_router)
api_v1_router.include_router(service_router)
api_v1_router.include_router(admin_crud_router)
api_v1_router.include_router(ocr_router)
api_v1_router.include_router(share_router)
api_v1_router.include_router(image_router)
api_v1_router.include_router(overview_router)
api_v1_router.include_router(persona_stat_router)
api_v1_router.include_router(sub_tool_stat_router)
api_v1_router.include_router(tool_stat_router)
api_v1_router.include_router(user_stat_router)
api_v1_router.include_router(extra_stat_router)
api_v1_router.include_router(payment_router)
api_v1_router.include_router(version_control_router)
api_v1_router.include_router(explore_router)
api_v1_router.include_router(ask_router)
