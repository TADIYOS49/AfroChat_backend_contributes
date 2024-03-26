from aiogram import Dispatcher
from .handlers import (
    handle_persona_callback,
    handle_persona_command,
    handle_persona_click_callback,
)
from .keyboards import persona_cb


def register_persona_features(bot: Dispatcher):
    bot.register_callback_query_handler(handle_persona_callback, text="personas")
    bot.register_message_handler(handle_persona_command, commands=["personas"])
    bot.register_callback_query_handler(
        handle_persona_click_callback, lambda c: c.data.startswith("persona")
    )
