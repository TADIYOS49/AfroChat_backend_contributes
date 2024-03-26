from aiogram import Bot, Dispatcher, executor


from app.bot.features import register_features
from config import initial_config

from config import initial_config


API_TOKEN = initial_config.TELEGRAM_BOT_TOKEN

WEBHOOK_PATH = f"/bot/{API_TOKEN}"
WEBHOOK_URL = initial_config.SERVICE_URL + WEBHOOK_PATH


if not API_TOKEN:
    raise Exception(
        "Telegram API token not found.\
        Set the TELEGRAM_API_TOKEN environment variable."
    )

bot = Bot(token=API_TOKEN, parse_mode="html")
dp = Dispatcher(bot)


register_features(dp)


def run_bot_with_pooling(dp: Dispatcher) -> None:
    executor.asyncio.create_task(dp.start_polling())
    pass
