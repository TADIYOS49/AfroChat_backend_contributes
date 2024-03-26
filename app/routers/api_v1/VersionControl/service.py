from http import HTTPStatus
from app.routers.api_v1.VersionControl.models import Version
import uuid


async def check_current_version(db_session, version):
    version_status = await Version.check_version(db_session, version)

    if version_status:
        return {"status": HTTPStatus.OK}

    else:
        return {"status": HTTPStatus.NOT_FOUND}


async def add_version(db_session, version):
    try:
        db_version: Version = Version(
            version_id=uuid.uuid4(), version=version, is_active=True
        )

        db_session.add(db_version)
        await db_session.commit()
        return db_version

    except Exception as e:
        print(e.__repr__())
        await db_session.rollback()
        raise e
