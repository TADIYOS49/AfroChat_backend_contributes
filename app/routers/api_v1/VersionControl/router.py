import hmac
from typing import Annotated, List
from app.routers.api_v1.VersionControl.exceptions import VERSION_NAME_ALREADY_EXISTS
from app.routers.api_v1.VersionControl.models import Version
from app.routers.api_v1.VersionControl.service import add_version, check_current_version
from fastapi import APIRouter, Body, Depends, Request
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import ujson
from app.database.database import get_db
from app.routers.api_v1.Auth.dependencies import get_activated_user, is_admin_user
from fastapi import APIRouter, Depends, Body, Path, Query


version_control_router = APIRouter(tags=["Version Control"])


@version_control_router.post(
    "/check-version",
)
async def check_version(
    version: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await check_current_version(db_session=db_session, version=version)


@version_control_router.post(
    "/add-new-version",
)
async def add_new_version(
    version: str,
    db_session: AsyncSession = Depends(get_db),
):
    db_version: Version | None = await Version.find_by_version_name(
        db_session=db_session,
        version=version,
    )
    if db_version:
        raise VERSION_NAME_ALREADY_EXISTS

    return await add_version(db_session=db_session, version=version)


@version_control_router.put(
    "/update-version-status",
)
async def update_version(
    version: str,
    is_active: bool,
    db_session: AsyncSession = Depends(get_db),
):
    db_version: Version | None = await Version.find_by_version_name(
        db_session=db_session,
        version=version,
    )

    db_version.is_active = is_active
    await db_version.save(db_session)

    return {
        "message": f"Version {version} status has been updated to {'active' if is_active else 'inactive'}."
    }
