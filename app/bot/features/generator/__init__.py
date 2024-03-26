from aiogram import Dispatcher
from .handlers import generate_command_handler


def register_generate_features(bot: Dispatcher):
    bot.register_message_handler(generate_command_handler, commands=["generate"])
