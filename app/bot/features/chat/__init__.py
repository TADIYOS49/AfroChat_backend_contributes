from aiogram import Dispatcher
from .handlers import handle_chat_callback, chat_command_handler


def register_chat_features(bot: Dispatcher):
    bot.register_callback_query_handler(handle_chat_callback, text="chat")
    bot.register_message_handler(chat_command_handler, commands=["chat"])
