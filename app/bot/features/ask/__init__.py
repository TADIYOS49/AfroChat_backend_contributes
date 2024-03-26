from aiogram import Dispatcher
from .handlers import handle_ask_callback, ask_command_handler


def register_ask_features(bot: Dispatcher):
    bot.register_callback_query_handler(handle_ask_callback, text="ask")
    bot.register_message_handler(ask_command_handler, commands=["ask"])
