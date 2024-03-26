from aiogram import Dispatcher
from app.bot.features.menu.handlers import (
    handle_mege_callback,
    handle_start_callback,
    start_handler,
    help_command_handler,
)


def register_main_menu_features(bot: Dispatcher):
    bot.register_message_handler(start_handler, commands=["start"])
    bot.register_message_handler(help_command_handler, commands=["help"])
    bot.register_callback_query_handler(handle_start_callback, text="start")
    bot.register_callback_query_handler(
        handle_mege_callback, lambda c: c.data.startswith("merge")
    )
