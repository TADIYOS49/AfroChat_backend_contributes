from sqlite3 import IntegrityError
from typing import Annotated, Any
from uuid import UUID
from app.routers.api_v1.Auth.models import (
    SignUpPlatform,
    User,
    UserTelegram,
    OtpReason,
    Phone_Otp,
)
from app.routers.api_v1.Auth.utils import generate_random_otp, validate_initData

from fastapi import APIRouter, Body, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.routers.api_v1.Auth.constants import PROFILE_AVATARS
from app.routers.api_v1.Auth.dependencies import (
    get_activated_user,
    is_admin_user,
    verify_reset_token,
)
from app.routers.api_v1.Auth.exceptions import (
    USER_ALREADY_ACTIVATED,
    USER_NAME_IS_TAKEN,
    EMAIL_HAS_BEEN_REGISTERED,
    PHONE_HAS_BEEN_REGISTERED,
    OTP_VALIDATION_FAILED,
    USER_NOT_ACTIVATED,
    USER_NOT_FOUND,
    TelegramIDAlreadyInUse,
    BotsNotAllowed,
)
from app.routers.api_v1.Auth.schemas import (
    LoginResponseModel,
    UserOut,
    UserCreate,
    OtpVerify,
    OtpVerifyWithPreferablePersona,
    UpdateUserProfile,
    TelegramAuthenticationSchema,
)
from app.routers.api_v1.Auth.service import (
    add_preferable_personas,
    authenticate_user,
    check_email_exists,
    check_phone_number_exists,
    create_access_and_refresh_token,
    create_new_user,
    deactivate_otp,
    generate_new_access_token,
    send_email_reset_otp,
    send_phone_reset_otp,
    send_sms,
    verify_email_otp,
    authenticate_user_with_google,
    verify_otp_code_reset,
    generate_reset_token,
    change_password,
    update_profile_change_username,
    update_profile_change_profile_pic,
    update_profile_change_password,
    verify_phone_otp,
    user_has_password,
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


@auth_router.post("/sign_up_check", response_model=dict[str, Any])
async def sign_up_check(
    user: Annotated[UserCreate, Body()], db_session: AsyncSession = Depends(get_db)
):
    db_user: User | None = await User.find_by_username(
        db_session=db_session, username=user.username
    )

    if db_user:
        raise USER_NAME_IS_TAKEN

    if await check_email_exists(db_session, user.email):
        raise EMAIL_HAS_BEEN_REGISTERED

    if await check_phone_number_exists(db_session, user.phone_number):
        raise PHONE_HAS_BEEN_REGISTERED

    return {"detail": "user is valid"}


@auth_router.post("/sign_up", response_model=UserOut, status_code=201)
async def sign_up(
    user: Annotated[UserCreate, Body()], db_session: AsyncSession = Depends(get_db)
):
    db_user: User | None = await User.find_by_username(
        db_session=db_session, username=user.username
    )

    if await check_email_exists(db_session, user.email):
        raise EMAIL_HAS_BEEN_REGISTERED

    if await check_phone_number_exists(db_session, user.phone_number):
        raise PHONE_HAS_BEEN_REGISTERED

    if db_user:
        # check if the user is activated
        if db_user.is_activated:
            raise USER_NAME_IS_TAKEN
        await db_user.delete(db_session)

    db_user = await create_new_user(db_session, user)
    if not db_user:
        raise USER_NOT_FOUND

    res = UserOut.from_orm(db_user)

    # check if the users has password
    res.has_password = await user_has_password(
        db_session=db_session, user_id=db_user.id
    )

    return res


@auth_router.get("/username/{username}", response_model=dict[str, Any])
async def check_username_availability(
    username: str, db_session: AsyncSession = Depends(get_db)
):
    db_user: User | None = await User.find_by_username(
        db_session=db_session, username=username
    )
    if db_user:
        return {"is_available": False}
    return {"is_available": True}


@auth_router.post("/login", response_model=LoginResponseModel)
async def login(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(get_db),
):
    user: User = await authenticate_user(db_session, login_data)
    user_schema = UserOut.from_orm(user)

    # check if the users has password
    user_schema.has_password = await user_has_password(
        db_session=db_session, user_id=user.id
    )

    # change the HttpUrl to str
    user_schema.profile_picture = str(user_schema.profile_picture)

    return create_access_and_refresh_token(data=user_schema.model_dump())


@auth_router.post("/refresh_token", response_model=LoginResponseModel)
async def generate_new_access_token_router(
    refresh_token: str = Header(..., embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    new_access_token: str = await generate_new_access_token(db_session, refresh_token)
    # returns the same refresh token
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@auth_router.post("/sign_in_with_google")
async def sign_in_with_google(
    access_token: str, db_session: AsyncSession = Depends(get_db)
):
    user: User = await authenticate_user_with_google(db_session, access_token)

    user_schema = UserOut.from_orm(user)

    # check if the users has password
    user_schema.has_password = await user_has_password(
        db_session=db_session, user_id=user.id
    )

    user_schema.profile_picture = str(user_schema.profile_picture)

    return create_access_and_refresh_token(data=user_schema.model_dump())


@auth_router.post("/activate")
async def activate_my_account(
    otp_verify: OtpVerify, db_session: AsyncSession = Depends(get_db)
):
    try:
        db_user: User | None = (
            await verify_phone_otp(db_session, otp_verify)
            if otp_verify.otp[0] < "5"
            else await verify_email_otp(db_session, otp_verify)
        )
        if db_user:
            user_schema = UserOut.from_orm(db_user)
            user_schema.profile_picture = str(user_schema.profile_picture)

            # check if the users has password
            user_schema.has_password = await user_has_password(
                db_session=db_session, user_id=db_user.id
            )

            access_token = create_access_and_refresh_token(
                data=user_schema.model_dump()
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_schema,
            }
        await db_session.rollback()
        raise OTP_VALIDATION_FAILED
    except Exception as e:
        await db_session.rollback()
        raise e


@auth_router.post("/activate_with_preferable_persona")
async def activate_my_account_with_persona(
    otp_verify: OtpVerifyWithPreferablePersona,
    db_session: AsyncSession = Depends(get_db),
):
    try:
        otp_user = OtpVerify(otp=otp_verify.otp, user_id=otp_verify.user_id)
        db_user: User | None = (
            await verify_phone_otp(db_session, otp_user)
            if otp_user.otp[0] < "5"
            else await verify_email_otp(db_session, otp_user)
        )
        if db_user:
            await add_preferable_personas(
                db_user, otp_verify.preferable_personas, db_session
            )
            user_schema = UserOut.from_orm(db_user)

            # check if the users has password
            user_schema.has_password = await user_has_password(
                db_session=db_session, user_id=db_user.id
            )

            user_schema.profile_picture = str(user_schema.profile_picture)
            return create_access_and_refresh_token(data=user_schema.model_dump())
        await db_session.rollback()
        raise OTP_VALIDATION_FAILED
    except Exception as e:
        await db_session.rollback()
        raise e


@auth_router.get("/user/me", response_model=UserOut)
async def my_account(
    user: Annotated[User, Depends(is_admin_user)],
):
    res = UserOut.from_orm(user)

    # check if the users has password
    res.has_password = await user_has_password(
        db_session=user.db_session, user_id=user.id
    )

    return res


@auth_router.put("/update_profile")
async def update_account(
    user: Annotated[User, Depends(get_activated_user)],
    new_user: Annotated[UpdateUserProfile, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    # FIXME: make this endpoint more efficient,
    #        by merging the db call into one

    # update the user
    user = await update_profile_change_username(
        new_user=new_user, db_session=db_session, user=user
    )

    # update profile picture
    user = await update_profile_change_profile_pic(
        new_user=new_user, db_session=db_session, user=user
    )

    # update password
    user_schema: UserOut = await update_profile_change_password(
        new_user=new_user, db_session=db_session, user=user
    )

    # create a new token
    user_schema.profile_picture = str(user_schema.profile_picture)

    # check if the users has password
    user_schema.has_password = await user_has_password(
        db_session=db_session, user_id=user.id
    )

    return create_access_and_refresh_token(data=user_schema.model_dump())


@auth_router.get("/profile_avatars", response_model=list[HttpUrl])
async def get_profile_avatars():
    return PROFILE_AVATARS


@auth_router.delete("/user/delete", response_model=dict[str, Any])
async def delete_my_account(
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    await user.delete(db_session)
    return {"detail": "data deleted"}


@auth_router.post("/resend_otp", response_model=UserOut)
async def resend_otp(user_id: UUID, db_session: AsyncSession = Depends(get_db)):
    otp_value: str = generate_random_otp(Type="phone")
    db_user: User | None = await User.find(db_session=db_session, user_id=user_id)

    if not db_user:
        raise USER_NOT_FOUND

    if db_user.is_activated:
        raise USER_ALREADY_ACTIVATED

    try:
        # Add the new user and OTP to the session
        # Commit the transaction
        await deactivate_otp(
            db_session=db_session,
            user_id=user_id,
            otp_reason=OtpReason.ACTIVATE.value,
            user_activation=False,
        )

        db_otp: Phone_Otp = Phone_Otp(
            user_id=user_id,
            phone_number=db_user.phone_numbers[0].phone_number,
            otp=otp_value,
            reason=OtpReason.ACTIVATE.value,
        )

        await send_sms(db_user.phone_numbers[0].phone_number, otp_value=otp_value)
        db_session.add(db_otp)
        await db_session.commit()

    except IntegrityError:
        # If an error occurred, roll back the transaction
        await db_session.rollback()
        raise

    res = UserOut.from_orm(db_user)

    # check if the users has password
    res.has_password = await user_has_password(db_session=db_session, user_id=user_id)

    return res


# password reset: takes user phone number and send otp
@auth_router.post("/forgot_password", response_model=UserOut, status_code=201)
async def forget_password(
    phone: str = Body(None, embed=True),
    email: str = Body(None, embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    db_user = None
    if phone:
        db_user: User | None = await User.find_by_phone_number(
            phone_number=phone, db_session=db_session
        )

        if db_user:
            if not db_user.is_activated:
                raise USER_NOT_ACTIVATED

            await send_phone_reset_otp(
                user_id=db_user.id, phone_number=phone, db_session=db_session
            )

    if email:
        db_user = await User.find_by_email(email=email, db_session=db_session)
        if not db_user:
            raise USER_NOT_FOUND

        if not db_user.is_activated:
            raise USER_NOT_ACTIVATED

        if db_user:
            await send_email_reset_otp(
                user_id=db_user.id, email=email, db_session=db_session
            )
    if not db_user:
        raise USER_NOT_FOUND

    # TODO: check if the user is authenticated. If not send activation otp
    # TODO: check if the user already has an otp

    res = UserOut.from_orm(db_user)

    # check if the users has password
    res.has_password = await user_has_password(
        db_session=db_session, user_id=db_user.id
    )
    return res


@auth_router.post("/verify_reset_otp", status_code=201)
async def verify_reset_otp(
    otp_verify: Annotated[OtpVerify, Body(...)],
    db_session: AsyncSession = Depends(get_db),
):
    try:
        # check if the otp is valid
        await verify_otp_code_reset(otp_verify=otp_verify, db_session=db_session)

        # generate a reset token
        reset_token = await generate_reset_token(
            db_session=db_session, user_id=otp_verify.user_id
        )
    except Exception as e:
        await db_session.rollback()
        raise e

    return {
        "reset_token": reset_token,
        "token_type": "bearer",
        "detail": "otp verified",
    }


# password reset: takes reset token and new password
@auth_router.put("/reset_password", status_code=201)
async def reset_password(
    user: Annotated[User, Depends(verify_reset_token)],
    new_password: str = Body(..., embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    await change_password(user=user, new_password=new_password, db_session=db_session)

    return {"detail": "password reset successful"}


# Add Validator Here
# TODO: Delete this endpoint
# @auth_router.post("/telegram_login")
# async def telegram_login(
#     schema: TelegramAuthenticationSchema,
#     db_session: AsyncSession = Depends(get_db),
# ):
#     is_valid, telegram_user = validate_initData(
#         schema.hash_str,
#         schema.initData,
#         schema.telegram_user,
#     )

#     if not is_valid:
#         raise InvalidTelegramCredentials

#     telegram_id: str = str(telegram_user.get("id", ""))

#     db_user: User | None = await User.find_by_telegram_id(
#         db_session=db_session, telegram_id=telegram_id
#     )

#     if not db_user:
#         return {
#             "auth": True,
#             "is_registered": False,
#         }
#     # if user already exists, Sign in
#     user_schema = UserOut.from_orm(db_user)

#     # # change the HttpUrl to str
#     user_schema.profile_picture = str(user_schema.profile_picture)

#     access_token = create_access_token(
#         data=user_schema.model_dump(), expires_delta=timedelta(weeks=1)
#     )

# return {
#     "access_token": access_token,
#     "token_type": "bearer",
#     "user": user_schema,
#     "auth": True,
#     "is_registered": True,
# }


@auth_router.post("/telegram_signin")
async def telegram_signin(
    data: TelegramAuthenticationSchema,
    db_session: AsyncSession = Depends(get_db),
):
    # validate that the request is coming from telegram
    telegram_user = validate_initData(data.hash_str, data.initData, data.telegram_user)

    if telegram_user.is_bot:
        raise BotsNotAllowed

    str_id: str = str(telegram_user.id)

    db_user: User | None = await User.find_by_telegram_id(
        db_session=db_session, telegram_id=str_id
    )
    if db_user.is_archived:
        raise TelegramIDAlreadyInUse

    # if user already exists, Sign in
    if db_user:
        user_schema = UserOut.from_orm(db_user)

        # # change the HttpUrl to str

        user_schema.profile_picture = str(user_schema.profile_picture)

        return create_access_and_refresh_token(data=user_schema.model_dump())

    # if user does not exist and have provided username, Sign up
    elif telegram_user.username:
        # check if the username is taken
        db_existing_user: User | None = await User.find_by_username(
            db_session=db_session, username=telegram_user.username
        )
        if db_existing_user:
            raise USER_NAME_IS_TAKEN

        new_user: User = User()
        new_user.username = telegram_user.username
        new_user.is_activated = True
        new_user.signup_platform = SignUpPlatform.TELEGRAM.value
        await new_user.save(db_session=db_session)

        new_user_telegram: UserTelegram = UserTelegram()
        new_user_telegram.telegram_id = str_id
        new_user_telegram.user_id = new_user.id
        new_user_telegram.full_name = telegram_user.full_name
        await new_user_telegram.save(db_session=db_session)

        db_user: User | None = await User.find_by_telegram_id(
            db_session=db_session, telegram_id=str_id
        )
        if not db_user:
            raise USER_NOT_FOUND

        user_schema = UserOut.from_orm(db_user)

        # # change the HttpUrl to str
        user_schema.profile_picture = str(user_schema.profile_picture)

        return create_access_and_refresh_token(data=user_schema.model_dump())
    else:
        raise USER_NOT_FOUND
