import aiohttp
import random
import re
import smtplib
import uuid
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Any, List
from uuid import UUID

from jose import jwt
from sqlalchemy import Select, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi.security import OAuth2PasswordRequestForm

from config import initial_config

from app.database.database import get_db_context
from app.routers.api_v1.Auth.exceptions import (
    ERROR_SENDING_SMS_MESSAGE,
    EMAIL_MUST_BE_PROVIDED,
    GOOGLE_AUTH_FAILED,
    INCORRECT_PASSWORD,
    INVALID_CREDENTIAL,
    OTP_EXPIRED,
    OTP_NOT_FOUND,
    OTP_VALIDATION_FAILED,
    PHONE_NUMBER_OR_EMAIL_MUST_BE_PROVIDED,
    SMTPAuthenticationError,
    TOKEN_EXPIRED,
    USER_DOESNT_HAVE_PASSWORD,
    USER_NAME_IS_TAKEN,
    USER_NOT_ACTIVATED,
    USER_NOT_FOUND,
)
from app.routers.api_v1.Auth.models import (
    AskTelegram,
    Email_Otp,
    OtpReason,
    Phone_Otp,
    PreferablePersona,
    SignUpPlatform,
    User,
    UserEmail,
    UserGeneratedImages,
    UserPassword,
    UserPhoneNumber,
    UserProfilePicture,
    UserTelegram,
)
from app.routers.api_v1.Auth.schemas import (
    OtpVerify,
    UpdateUserProfile,
    UserCreate,
    UserOut,
)
from app.routers.api_v1.Auth.utils import (
    generate_random_otp,
    generate_random_username,
    hash_password,
    has_time_passed,
    verify_password,
)
from app.routers.api_v1.chat.models import ChatSession
from app.utils.logger import FastApiLogger

from .constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    GOOGLE_CLIENT_ID_1,
    GOOGLE_CLIENT_ID_2,
    GOOGLE_CLIENT_ID_3,
    OTP_SENDER_EMAIL,
    PROFILE_AVATARS,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    SENDER_PASSWORD,
    SMS_API_KEY,
    SMS_URL,
)
from app.routers.api_v1.Persona.models import Persona


async def send_sms(phone_number: str, otp_value: str) -> bool:
    url = SMS_URL
    payload = {
        "token": SMS_API_KEY,
        "phone": phone_number,
        "msg": otp_value,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            response = await response.json()
            if response["error"]:
                raise ERROR_SENDING_SMS_MESSAGE
            return True


async def verify_recaptcha(
    token: str,
    user_ip: str | None = None,
    secret_key: str = initial_config.reCAPTCHA_V3_SECRET_KEY,
) -> bool:
    """
    Verifies a reCAPTCHA token using the Google reCAPTCHA v3 API.

    Args:
        token: The reCAPTCHA token obtained from the request header.
        user_ip: The user's IP address.
        secret_key: Your reCAPTCHA v3 secret key.

    Returns:
        True if the token is valid, False otherwise.
    """

    data = {
        "secret": secret_key,
        "response": token,
        "remoteip": user_ip if user_ip else "",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            initial_config.RECAPTCHA_VERIFY_URL, data=data
        ) as response:
            if response.status != 200:
                raise Exception("Failed to verify reCAPTCHA token")
            response_json = await response.json()
            return (
                response_json.get("success", False)
                and response_json.get("score", 0) >= 0.5
            )


async def send_email(recipient_email: str, otp_value: str):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(OTP_SENDER_EMAIL, SENDER_PASSWORD)
        message = EmailMessage()
        message["Subject"] = "Afrochat otp verification"
        message["From"] = "Afrochat"
        message["To"] = recipient_email

        message.set_content("Your OTP is: " + otp_value)
        server.send_message(message)

    except smtplib.SMTPAuthenticationError:
        raise SMTPAuthenticationError


async def check_email_exists(db_session: AsyncSession, email: str | None):
    if not email:
        return False

    db_user = await User.find_by_email(db_session=db_session, email=email)

    if db_user:
        if db_user.is_activated:
            return True
        else:
            await db_user.delete(db_session=db_session)

    return False


async def check_phone_number_exists(db_session: AsyncSession, phone_number: str | None):
    if not phone_number:
        return False

    db_user = await User.find_by_phone_number(
        db_session=db_session, phone_number=phone_number
    )

    if db_user:
        if db_user.is_activated:
            return True
        else:
            await db_user.delete(db_session=db_session)

    return False


def create_access_and_refresh_token(data: dict):
    to_encode = data.copy()
    access_token_expire_time = datetime.utcnow() + timedelta(
        seconds=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expire_time = datetime.utcnow() + timedelta(
        seconds=REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": access_token_expire_time})
    to_encode.update({"id": to_encode.get("id", "").hex})
    # pop created_at operation
    to_encode.pop("created_at")
    to_encode.pop("has_password")

    access_token_encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    to_encode.update({"exp": refresh_token_expire_time})
    refresh_token_encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "access_token": access_token_encoded_jwt,
        "refresh_token": refresh_token_encoded_jwt,
        "token_type": "bearer",
        "user": data,
    }


def create_access_token(data: dict, expire_time: int | None):
    to_encode = data.copy()
    access_token_expire_time = datetime.utcnow() + timedelta(
        seconds=ACCESS_TOKEN_EXPIRE_MINUTES if not expire_time else expire_time
    )
    to_encode.update({"exp": access_token_expire_time})
    to_encode.update({"id": to_encode.get("id", "").hex})
    # pop created_at operation
    to_encode.pop("created_at")
    access_token_encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return access_token_encoded_jwt


async def create_new_user(db_session: AsyncSession, user: UserCreate):
    avatar_picture = random.choice(PROFILE_AVATARS)

    if not user.phone_number and not user.email:
        raise PHONE_NUMBER_OR_EMAIL_MUST_BE_PROVIDED

    try:
        new_user_id = uuid.uuid4()
        db_user: User = User(
            id=new_user_id,
            username=user.username,
        )

        to_be_added: list[Any] = [db_user]
        db_otp = None

        if not user.email:
            raise EMAIL_MUST_BE_PROVIDED

        if user.email:
            db_email = UserEmail(email=user.email, user_id=new_user_id)
            to_be_added.append(db_email)

            if not db_otp:
                otp_value = generate_random_otp(Type="email")
                db_otp = Email_Otp(
                    email=user.email,
                    user_id=new_user_id,
                    otp=otp_value,
                    reason=OtpReason.ACTIVATE.value,
                )
                to_be_added.append(db_otp)
                await send_email(recipient_email=user.email, otp_value=otp_value)

        if user.phone_number:
            db_phone_number = UserPhoneNumber(
                phone_number=user.phone_number, user_id=new_user_id
            )

            otp_value = generate_random_otp(Type="phone")
            # await send_sms(user.phone_number, otp_value=otp_value)

            db_otp = Phone_Otp(
                phone_number=user.phone_number,
                otp=otp_value,
                user_id=new_user_id,
                reason=OtpReason.ACTIVATE.value,
            )

            to_be_added += [db_phone_number, db_otp]

        db_password = UserPassword(
            hashed_password=hash_password(user.password), user_id=new_user_id
        )
        db_profile_picture = UserProfilePicture(
            profile_picture=avatar_picture, user_id=new_user_id
        )

        to_be_added += [db_password, db_profile_picture]

        db_session.add_all(to_be_added)
        await db_session.commit()
    except IntegrityError:
        # If an error occurred, roll back the transaction
        await db_session.rollback()
        raise

    final_db_user: User | None = await User.find(
        db_session=db_session,
        user_id=new_user_id,
    )
    return final_db_user


"""
Authenticate the User
"""


async def authenticate_user(db_session, login_data: OAuth2PasswordRequestForm):
    user_unique_identifier = login_data.username
    user: User | None

    phone_pattern = re.compile(r"^\+?251|^0\d{9}$")

    # check if the user is using username, email or phone number
    if "@" in user_unique_identifier:
        user: User | None = await User.find_by_email(db_session, user_unique_identifier)
    elif phone_pattern.match(user_unique_identifier):
        # if starts with '0' replace it with '+251'
        if user_unique_identifier[0] == "0":
            user_unique_identifier = "+251" + user_unique_identifier[1:]

        user: User | None = await User.find_by_phone_number(
            db_session, user_unique_identifier
        )
    else:
        user: User | None = await User.find_by_username(
            db_session, user_unique_identifier
        )

    if not user:
        raise USER_NOT_FOUND
    if not user.is_activated:
        raise USER_NOT_ACTIVATED
    if not user.password:
        raise USER_DOESNT_HAVE_PASSWORD
    if not verify_password(
        plain_password=login_data.password,
        hashed_password=user.password.hashed_password,
    ):
        raise INCORRECT_PASSWORD
    return user


async def verify_phone_otp(db_session, otp_verify: OtpVerify):
    stmt = (
        Select(Phone_Otp)
        .join(User, User.id == Phone_Otp.user_id)
        .options(selectinload(Phone_Otp.phone_number_instance))
        .where(
            User.id == otp_verify.user_id,
            Phone_Otp.reason == OtpReason.ACTIVATE.value,
            ~User.is_activated,
            ~Phone_Otp.is_used,
        )
    )

    res = await db_session.execute(stmt)
    otp: Phone_Otp | None = res.scalars().one_or_none()

    if not otp:
        raise OTP_NOT_FOUND

    if has_time_passed((otp.created_at + timedelta(days=3)).timestamp()):
        raise OTP_EXPIRED

    if otp.otp != otp_verify.otp:
        raise OTP_VALIDATION_FAILED

    # update the data for the OTP
    otp.is_used = True
    otp.phone_number_instance.is_activated = True
    db_user = await User.find(db_session=db_session, user_id=otp.user_id)

    if not db_user:
        raise USER_NOT_FOUND

    db_user.is_activated = True

    await db_session.commit()

    return db_user


async def verify_email_otp(db_session, otp_verify: OtpVerify):
    stm = (
        Select(Email_Otp)
        .join(User, User.id == Email_Otp.user_id)
        .options(selectinload(Email_Otp.email_instance))
        .where(
            User.id == otp_verify.user_id,
            Email_Otp.reason == OtpReason.ACTIVATE.value,
            ~User.is_activated,
            ~Email_Otp.is_used,
        )
    )

    res = await db_session.execute(stm)
    otp: Email_Otp = res.scalars().first()

    if not otp:
        raise OTP_NOT_FOUND

    if has_time_passed((otp.created_at + timedelta(days=3)).timestamp()):
        raise OTP_EXPIRED

    if otp.otp != otp_verify.otp:
        raise OTP_VALIDATION_FAILED

    # update the data for the OTP
    otp.is_used = True
    otp.email_instance.is_activated = True
    db_user = await User.find(db_session=db_session, user_id=otp.user_id)
    if not db_user:
        raise USER_NOT_FOUND
    db_user.is_activated = True

    await db_session.commit()

    return db_user


async def deactivate_otp(
    db_session,
    user_id: UUID,
    otp_reason: int,
    user_activation: bool,
):
    stm = (
        Select(Phone_Otp)
        .join(User, User.id == Phone_Otp.user_id)
        .options(selectinload(Phone_Otp.user))
        .where(
            User.id == user_id,
            Phone_Otp.reason == otp_reason,
            User.is_activated == user_activation,
        )
    )

    res = await db_session.execute(stm)
    phone_otps: List[Phone_Otp] = res.scalars().all()

    for otp in phone_otps:
        # update the data for the OTP
        otp.is_used = True

    stm = (
        Select(Email_Otp)
        .join(User, User.id == Email_Otp.user_id)
        .options(selectinload(Email_Otp.user))
        .where(
            User.id == user_id,
            Email_Otp.reason == otp_reason,
            User.is_activated == user_activation,
        )
    )

    res = await db_session.execute(stm)
    email_otps: List[Email_Otp] = res.scalars().all()

    for otp in email_otps:
        # update the data for the OTP
        otp.is_used = True

    await db_session.commit()

    return


async def add_preferable_personas(
    user: User, personas: List[UUID], db_session: AsyncSession
):
    try:
        stmt = select(Persona.id).filter(Persona.id.in_(personas))
        result = await db_session.execute(stmt)

        for persona_id in result.scalars().all():
            db_preferable_persona: PreferablePersona | None = (
                await PreferablePersona.find_by_user_id_and_persona_id(
                    db_session=db_session, user_id=user.id, persona_id=persona_id
                )
            )
            if not db_preferable_persona:
                db_preferable_persona = PreferablePersona(
                    user_id=user.id, persona_id=persona_id
                )
                db_session.add(db_preferable_persona)

        await db_session.commit()

    except Exception as ex:
        await db_session.rollback()
        raise ex

    return {"message": "Favorite personas added successfully"}


async def validate_google_access_token(access_token: str) -> dict[str, Any]:
    url = "https://oauth2.googleapis.com/tokeninfo"
    params = {"access_token": access_token}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    raise Exception()

    except Exception:
        # Handle the exception here other exceptions here
        raise GOOGLE_AUTH_FAILED


async def authenticate_user_with_google(db_session: AsyncSession, access_token: str):
    user_data: dict[str, Any] = await validate_google_access_token(access_token)
    # check if the client id is the same as the one in the data

    if (
        user_data.get("aud") != GOOGLE_CLIENT_ID_1
        and user_data.get("aud") != GOOGLE_CLIENT_ID_2
        and user_data.get("aud") != GOOGLE_CLIENT_ID_3
    ):
        raise GOOGLE_AUTH_FAILED
    # check if time has passed
    if has_time_passed(int(user_data.get("exp", ""))):
        raise GOOGLE_AUTH_FAILED

    user_email = user_data.get("email", "")
    user = await User.find_by_email(db_session=db_session, email=user_email)
    if not user:
        try:
            new_user_id = uuid.uuid4()
            db_user = User(
                id=new_user_id,
                username=generate_random_username(),
                is_activated=True,
            )

            db_email = UserEmail(
                email=user_email, user_id=new_user_id, is_activated=True
            )

            avatar_picture = random.choice(PROFILE_AVATARS)
            db_profile_picture = UserProfilePicture(
                profile_picture=avatar_picture,
                user_id=new_user_id,
            )
            db_session.add_all([db_user, db_email, db_profile_picture])
            await db_session.commit()
            user = await User.find(db_session=db_session, user_id=new_user_id)
        except IntegrityError:
            await db_session.rollback()
            raise
    return user


# Send password reset otp
async def send_phone_reset_otp(
    user_id: UUID, phone_number: str, db_session: AsyncSession
) -> None:
    # first deactivate existing OTPs
    FastApiLogger.debug(user_id)
    FastApiLogger.debug(phone_number)
    await deactivate_otp(
        db_session=db_session,
        user_id=user_id,
        otp_reason=OtpReason.RESET_PASSWORD.value,
        user_activation=True,
    )

    otp_value = generate_random_otp(Type="phone")
    # create a password reset token
    otp = Phone_Otp(
        user_id=user_id,
        reason=OtpReason.RESET_PASSWORD.value,
        otp=otp_value,
        phone_number=phone_number,
    )

    # send sms of the otp
    await send_sms(phone_number=phone_number, otp_value=otp_value)

    await otp.save(db_session=db_session)


async def send_email_reset_otp(
    user_id: UUID, email: str, db_session: AsyncSession
) -> None:
    # first deactivate existing OTPs
    await deactivate_otp(
        db_session=db_session,
        user_id=user_id,
        otp_reason=OtpReason.RESET_PASSWORD.value,
        user_activation=True,
    )

    otp_value = generate_random_otp(Type="email")
    # create a password reset token
    otp = Email_Otp(
        user_id=user_id,
        reason=OtpReason.RESET_PASSWORD.value,
        otp=otp_value,
        email=email,
    )

    # send sms of the otp
    await send_email(recipient_email=email, otp_value=otp_value)

    await otp.save(db_session=db_session)


async def verify_otp_code_reset(otp_verify: OtpVerify, db_session: AsyncSession):
    otp: Phone_Otp | Email_Otp | None = (
        await Phone_Otp.find_otp_by_active_user(
            db_session=db_session,
            user_id=otp_verify.user_id,
            otp_reason=OtpReason.RESET_PASSWORD.value,
        )
        if otp_verify.otp[0] < "5"
        else await Email_Otp.find_otp_by_active_user(
            db_session=db_session,
            user_id=otp_verify.user_id,
            otp_reason=OtpReason.RESET_PASSWORD.value,
        )
    )

    if not otp:
        raise OTP_NOT_FOUND

    if has_time_passed((otp.created_at + timedelta(minutes=5)).timestamp()):
        raise OTP_EXPIRED

    if otp.otp != otp_verify.otp:
        raise OTP_VALIDATION_FAILED

    # update the data for the OTP
    otp.is_used = True
    await db_session.commit()

    return otp.user


async def generate_reset_token(db_session: AsyncSession, user_id: UUID) -> str:
    user = await User.find(db_session=db_session, user_id=user_id)
    if not user:
        raise USER_NOT_FOUND

    return create_access_token(
        data={"id": user.id, "username": user.username, "created_at": user.created_at},
        expire_time=None,
    )


async def generate_new_access_token(db_session: AsyncSession, refresh_token: str):
    try:
        payload: dict[str, Any] = jwt.decode(refresh_token, SECRET_KEY)
        if has_time_passed(payload["exp"]):
            raise TOKEN_EXPIRED

        user: User | None = await User.find(
            db_session=db_session, user_id=UUID(hex=payload["id"])
        )

        if not user:
            raise INVALID_CREDENTIAL

        user_schema = UserOut.from_orm(user)
        # change the HttpUrl to str
        user_schema.profile_picture = str(user_schema.profile_picture)

        return create_access_token(
            data=user_schema.model_dump(),
            expire_time=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    except Exception as e:
        if e.__class__.__name__ == "ExpiredSignatureError":
            raise TOKEN_EXPIRED
        raise INVALID_CREDENTIAL


async def change_password(
    user: User, new_password: str, db_session: AsyncSession
) -> User:
    # Check if the user has a password
    if not user.password:
        # Create a new password if user doesn't have a password
        db_password = UserPassword(
            hashed_password=hash_password(new_password), user_id=user.id
        )
        await db_password.save(db_session)
    else:
        # change the password of provided user
        # and hash the new password
        user.password.hashed_password = hash_password(new_password)
        await user.password.save(db_session)

    return user


async def update_profile_change_username(
    new_user: UpdateUserProfile, db_session: AsyncSession, user: User
) -> User:
    if not new_user.username or user.username == new_user.username:
        return user
    db_user: User | None = await User.find_by_username(
        db_session=db_session, username=new_user.username
    )

    if db_user:
        raise USER_NAME_IS_TAKEN

    user.username = new_user.username
    await user.save(db_session=db_session)

    return user


async def update_profile_change_profile_pic(
    new_user: UpdateUserProfile, db_session: AsyncSession, user: User
) -> User:
    if not new_user.profile_picture:
        return user
    user.profile_picture.profile_picture = str(new_user.profile_picture)

    await user.profile_picture.save(db_session=db_session)

    return user


async def update_profile_change_password(
    new_user: UpdateUserProfile, db_session: AsyncSession, user: User
) -> UserOut:
    if not new_user.new_password:
        res = UserOut.from_orm(user)

        # check if the user have a password
        res.has_password = await user_has_password(
            user_id=user.id, db_session=db_session
        )
        return res

    # check if the user have a password
    if await user_has_password(user_id=user.id, db_session=db_session):
        if not new_user.old_password:
            raise INCORRECT_PASSWORD
        if not verify_password(new_user.old_password, user.password.hashed_password):
            raise INCORRECT_PASSWORD

    user = await change_password(
        user=user, new_password=new_user.new_password, db_session=db_session
    )

    user_schema = UserOut.from_orm(user)
    user_schema.profile_picture = str(user_schema.profile_picture)

    return user_schema


async def create_new_telegram_user(
    db_session: AsyncSession,
    telegram_id: str,
    username: str,
    full_name: str,
) -> User:
    new_user: User = User(
        username=username,
        is_activated=True,
        signup_platform=SignUpPlatform.TELEGRAM.value,
    )
    db_session.add(new_user)

    await db_session.flush()
    new_user_telegram: UserTelegram = UserTelegram(
        telegram_id=telegram_id,
        full_name=full_name,
        user_id=new_user.id,
    )
    db_session.add(new_user_telegram)
    try:
        await db_session.commit()
        return new_user
    except SQLAlchemyError as e:
        await db_session.rollback()
        raise e


async def check_if_it_can_be_merged(telegram_id: str, user_id: uuid.UUID):
    try:
        async with get_db_context() as db_session:
            # Check if both users exist
            db_mobile_user = await User.find(db_session=db_session, user_id=user_id)
            if not db_mobile_user:
                raise Exception("User not found")

            db_telegram_user = await User.find_by_telegram_id(
                db_session=db_session, telegram_id=telegram_id
            )

            if not db_telegram_user:
                # if telegram_id_already doesn't exist then i can create a new one
                return {"message": "Telegram account not found"}

            # if the telegram_id have been linked with another account should we
            if db_telegram_user.phone_numbers or db_telegram_user.emails:
                # one telegram_id can only have one user_id
                raise Exception("Telegram account already merged")

            if db_telegram_user.id != db_mobile_user.id:
                return {"message": "Accounts can be merged"}
            raise Exception("This account has been already merged with the same user")
    except Exception as e:
        raise e


async def merge_accounts(telegram_id: str, full_name: str, user_id: uuid.UUID):
    try:
        async with get_db_context() as db_session:
            # Check if both users exist
            db_mobile_user = await User.find(db_session=db_session, user_id=user_id)
            if not db_mobile_user:
                raise Exception("User not found")

            db_telegram_user = await User.find_by_telegram_id(
                db_session=db_session, telegram_id=telegram_id
            )

            if not db_telegram_user:
                new_user_telegram = UserTelegram(
                    telegram_id=telegram_id,
                    user_id=db_mobile_user.id,
                    full_name=full_name,
                )

                await new_user_telegram.save(db_session=db_session)
                return {"message": "Telegram Account Created"}

            # if the telegram_id have been linked with another account should we
            if db_telegram_user.phone_numbers or db_telegram_user.emails:
                raise Exception("Telegram account already merged")

            if db_telegram_user.id != db_mobile_user.id:
                await replace_id(db_telegram_user.id, db_mobile_user.id, db_session)
                await db_session.delete(db_telegram_user)
                await db_session.commit()

                user_telegram = UserTelegram(
                    telegram_id=telegram_id,
                    user_id=db_mobile_user.id,
                    full_name=full_name,
                )

                await user_telegram.save(db_session=db_session)
                return {"message": "Accounts successfully merged"}

            return {"message": "Accounts already merged"}
    except Exception as e:
        raise e


async def replace_id(telegram_user_id, mobile_user_id, db_session):
    # Update AskTelegram
    await db_session.execute(
        update(AskTelegram)
        .where(AskTelegram.user_id == telegram_user_id)
        .values(user_id=mobile_user_id)
    )

    # Update UserTelegram
    await db_session.execute(
        update(UserTelegram)
        .where(UserTelegram.user_id == telegram_user_id)
        .values(user_id=mobile_user_id)
    )

    # Update ChatSession
    await db_session.execute(
        update(ChatSession)
        .where(ChatSession.user_id == telegram_user_id)
        .values(user_id=mobile_user_id)
    )

    # Update UserGeneratedImages
    await db_session.execute(
        update(UserGeneratedImages)
        .where(UserGeneratedImages.user_id == telegram_user_id)
        .values(user_id=mobile_user_id)
    )

    await db_session.commit()


async def user_has_password(user_id: UUID, db_session: AsyncSession):
    stmt = select(UserPassword).where(UserPassword.user_id == user_id).limit(1)
    res = await db_session.execute(stmt)
    user_password: UserPassword | None = res.scalars().one_or_none()

    if not user_password:
        return False
    return True
