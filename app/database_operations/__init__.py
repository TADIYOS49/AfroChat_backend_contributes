from sqlalchemy.exc import SQLAlchemyError


from app.database.database import get_db_context
from app.routers.api_v1.Auth.models import User, UserTelegram
from app.routers.api_v1.Auth.service import create_new_telegram_user


async def get_or_create_user(
    telegram_id: str,
    username: str,
    full_name: str,
) -> User:
    try:
        async with get_db_context() as db_session:
            # Check if a User with the given telegram_id exists

            telegram_user: User | None = await User.find_by_telegram_id(
                db_session, telegram_id
            )

            if not telegram_user:
                user = await create_new_telegram_user(
                    db_session=db_session,
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name,
                )
                return user
                # If the User does not exist, create a new User
                # telegram_user = await craete_new_

            return telegram_user
    except SQLAlchemyError as e:
        raise e


async def get_user_id_for_telegram(
    telegram_id: str,
):
    try:
        async with get_db_context() as db_session:
            # Check if a User with the given telegram_id exists
            telegram_user: UserTelegram | None = await UserTelegram.find_no_join(
                db_session, telegram_id
            )
            if not telegram_user:
                return None
            return telegram_user.user_id
    except SQLAlchemyError as e:
        raise e
