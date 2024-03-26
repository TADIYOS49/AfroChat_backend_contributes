import uuid
from app.routers.api_v1.Auth.exceptions import (
    EMAIL_HAS_BEEN_REGISTERED,
    PHONE_HAS_BEEN_REGISTERED,
    USER_NAME_IS_TAKEN,
    USER_NOT_FOUND,
)
from app.routers.api_v1.Auth.models import (
    Role,
    User,
    UserEmail,
    UserInfo,
    UserPhoneNumber,
)
from app.routers.api_v1.Auth.service import (
    check_email_exists,
    check_phone_number_exists,
)
from app.routers.api_v1.Auth.utils import hash_password, verify_password
from app.routers.api_v1.User.exceptions import PERMISSION_NOT_ALLOWED
from app.routers.api_v1.User.schemas import UpdateUserProfileAdmin, UserCreateAdmin
from sqlalchemy.ext.asyncio import AsyncSession


async def create_new_user(
    db_session: AsyncSession, new_user: UserCreateAdmin, creator: User
):
    db_user: User | None = await User.find_by_username(
        db_session=db_session, username=new_user.username
    )
    if db_user:
        raise USER_NAME_IS_TAKEN

    if await check_email_exists(db_session, new_user.email):
        raise EMAIL_HAS_BEEN_REGISTERED

    if new_user.phone_number and await check_phone_number_exists(
        db_session, new_user.phone_number
    ):
        raise PHONE_HAS_BEEN_REGISTERED

    if Role[new_user.role].value >= creator.role:
        raise PERMISSION_NOT_ALLOWED

    try:
        new_user_id = uuid.uuid4()

        db_user = User(
            id=new_user_id, username=new_user.username, role=Role[new_user.role].value
        )

        db_email = UserEmail(user_id=new_user_id, email=new_user.email)

        db_user_info = UserInfo(
            user_id=new_user_id,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            creator_id=creator.id,
        )

        db_session.add_all([db_user, db_email, db_user_info])

        if new_user.phone_number:
            db_phone_number = UserPhoneNumber(
                user_id=new_user_id, phone_number=new_user.phone_number
            )
            db_session.add(db_phone_number)

        # TODO create the registration link
        # registration_link = "some link"
        # send_email(recipient_email=new_user.email, otp_value=registration_link)

        await db_session.commit()
        db_user = await User.find(db_session=db_session, user_id=new_user_id)
        if not db_user:
            raise USER_NOT_FOUND
        return db_user
    except Exception as ex:
        await db_session.rollback()
        raise ex


async def update_user_service(
    db_session: AsyncSession, new_user: UpdateUserProfileAdmin, updator: User
):
    db_user = await User.find(new_user.user_id)
    if not db_user:
        raise USER_NOT_FOUND

    if db_user.role >= updator.role:
        raise PERMISSION_NOT_ALLOWED

    if new_user.username:
        db_user.username = new_user.username

    if new_user.profile_picture:
        if db_user.profile_picture:
            db_user.profile_picture.profile_picture = new_user.profile_picture

        # TODO if not db_user.profile_picture

    if new_user.new_password:
        if db_user.password:
            db_user.password.hashed_password = hash_password(new_user.new_password)

        # TODO if not db_user.password

    # TODO implement update first name and last name

    return db_user
