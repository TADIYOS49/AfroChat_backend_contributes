import logging
import os
from logging import Logger, FileHandler


def log_creator(logger_name: str) -> logging.Logger:
    os.makedirs("logs", exist_ok=True)

    logger: Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # create a loger handler
    # FIXME change the w to a during deployment

    handler: FileHandler = logging.FileHandler(f"logs/{logger_name}.log", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    return logger


FastApiLogger = log_creator("fastapi")
SQLAlchemyLogger = log_creator("sqlalchemy")
TelegramBotLogger = log_creator("telegram_bot")
