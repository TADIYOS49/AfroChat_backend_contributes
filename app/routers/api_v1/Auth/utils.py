import datetime
import hmac
from urllib.parse import unquote
from random import random
import hashlib
from app.routers.api_v1.Auth.exceptions import (
    TelegramValidationFailed,
    InvalidTelegramCredentials,
)
from app.routers.api_v1.Auth.schemas import TelegramUserAuth
from config import initial_config

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def has_time_passed(time_to_check):
    current_time = datetime.datetime.utcnow().timestamp()
    return current_time > time_to_check


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def generate_random_otp(Type: str, n: int = 4) -> str:
    first_digit = int(random() * 5) if Type == "phone" else (int(random() * 5) + 5)
    otp_value: str = str(first_digit) + "".join(
        [str(int(random() * 10)) for _ in range(n - 1)]
    )
    return otp_value


def generate_random_username():
    return f"User{int(random() * 100000000)}"


def validate_initData(
    hash_str: str,
    init_data: str,
    telegram_user: TelegramUserAuth,
    token=initial_config.TELEGRAM_VALIDATOR_TOKEN,
    c_str="WebAppData",
) -> TelegramUserAuth:
    """
    Validates the data received from the Telegram web app, using the
    method documented here:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    hash_str - the hash string passed by the webapp
    init_data - the query string passed by the webapp
    token - Telegram bot's token
    c_str - constant string (default = "WebAppData")
    """

    try:
        init_data = sorted(
            [
                chunk.split("=")
                for chunk in unquote(init_data).split("&")
                if chunk[: len("hash=")] != "hash="
            ],
            key=lambda x: x[0],
        )

        init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

        secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()
        data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

        if not data_check.hexdigest() == hash_str:
            raise InvalidTelegramCredentials

        return telegram_user
    except Exception as exc:
        if isinstance(exc, InvalidTelegramCredentials):
            raise exc
        raise TelegramValidationFailed
