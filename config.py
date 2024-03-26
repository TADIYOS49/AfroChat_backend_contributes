import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=".env")


class Config(BaseSettings):
    CONFIG_TYPE: str = ""
    CORS_ORGINS: list[str] = ["*"]

    SERVICE_URL: str = os.environ.get(
        "SERVICE_URL",
        "https://afrochat-bot-telegram-ij7jnmwh2q-zf.a.run.app",
    )
    MINI_APP_URL: str = os.environ.get(
        "MINI_APP_URL",
        "https://afrochat-bot-telegram-ij7jnmwh2q-zf.a.run.app/#/",
    )

    # DATABSE CONFIG
    POSTGRES_URL: str = os.environ.get("DATABASE_URL", "")
    DATABASE_POOL_RECYCLE: int = int(os.environ.get("DATABASE_POOL_RECYCLE", 900))
    DATABSE_POOL_SIZE: int = int(os.environ.get("DATABSE_POOL_SIZE", 20))
    DATABSE_POOL_OVERFLOW: int = int(os.environ.get("DATABSE_POOL_OVERFLOW", 20))

    TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    BOT_NAME: str = os.environ.get("BOT_NAME", "")

    # LLM API KEYS
    GOOGLE_GEMINI_API: str = os.environ.get("GOOGLE_GEMINI_API", "")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    # OAuth
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    GOOGLE_CLIENT_ID_1: str = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_ID_2: str = os.environ.get("GOOGLE_CLIENT_ID_2", "")
    GOOGLE_CLIENT_ID_3: str = os.environ.get("GOOGLE_CLIENT_ID_3", "")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 50)
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS ", 50)
    )

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.environ.get("CLOUDINARY_API_SECRET", "")

    # SMS SERVICE
    SMS_API_KEY: str = os.environ.get("SMS_API_KEY", "")
    SMS_URL: str = os.environ.get("SMS_URL", "")

    # max image size (3MB) # TODO: move to .env
    MAX_IMAGE_SIZE: int = 1024 * 1024 * 3
    OCR_SPACE_API: str = os.environ.get("OCR_SPACE_API", "")

    IMAGE_GENERATOR_API: str = os.environ.get("IMAGE_GENERATOR_API", "")
    IMAGE_GENERATOR_LIMIT: int = int(os.environ.get("IMAGE_GENERATOR_LIMIT", 50))

    TELEGRAM_VALIDATOR_TOKEN: str = os.environ.get(
        "TELEGRAM_VALIDATOR_TOKEN", TELEGRAM_BOT_TOKEN
    )

    OTP_SENDER_EMAIL: str = os.environ.get("OTP_SENDER_EMAIL", "")
    SENDER_PASSWORD: str = os.environ.get("SENDER_PASSWORD", "")
    MAX_REQUESTS_PER_DAY: int = int(os.environ.get("MAX_REQUESTS_PER_DAY", 20))
    MAX_DALL_E_REQUESTS_PER_DAY: int = int(
        os.environ.get("MAX_DALL_E_REQUESTS_PER_DAY", 10)
    )
    MAX_PERSONA_CREATION_PER_DAY: int = int(
        os.environ.get("MAX_PERSONA_CREATION_PER_DAY", 10)
    )

    # NEWS API KEY
    NEWS_API_KEY: str = os.environ.get("NEWS_API_KEY", "")

    #### PAYMENT GATEWAYS
    CHAPA_SECRET_KEY: str = os.environ.get("CHAPA_SECRET_KEY", "")
    CHAPA_URL: str = os.environ.get(
        "CHAPA_URL", "https://api.chapa.co/v1/transaction/initialize"
    )
    CHAPA_SECRET_HASH: str = os.environ.get("CHAPA_SECRET_HASH", "")

    GROUP_CHAT_MESSAGE_LIMIT: int = int(os.environ.get("GROUP_CHAT_MESSAGE_LIMIT", 100))

    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

    reCAPTCHA_V3_SITE_KEY: str = os.environ.get("reCAPTCHA_V3_SITE_KEY", "")
    reCAPTCHA_V3_SECRET_KEY: str = os.environ.get("reCAPTCHA_V3_SECRET_KEY", "")

    RECAPTCHA_VERIFY_URL: str = "https://www.google.com/recaptcha/api/siteverify"


class ProductionConfig(Config):
    CONFIG_TYPE: str = "production"
    pass


class DevConfing(Config):
    CONFIG_TYPE: str = "development"
    pass


class TestConfig(Config):
    CONFIG_TYPE: str = "test"
    POSTGRES_URL: str = os.environ.get("TEST_DATABASE_URL", "")


def get_settings(config_type: str = os.environ.get("CONFIG", "dev")) -> Config:
    if config_type == "dev":
        return DevConfing()
    if config_type == "test":
        return TestConfig()
    return ProductionConfig()


initial_config = get_settings()
tests_config = get_settings("test")
print(initial_config.CONFIG_TYPE)
