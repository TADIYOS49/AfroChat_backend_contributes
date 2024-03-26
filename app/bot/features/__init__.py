from aiogram import Dispatcher
from app.bot.features.generator import register_generate_features
from app.bot.features.ask import register_ask_features
from app.bot.features.menu import register_main_menu_features
from app.bot.features.global_handler import register_global_handler
from app.bot.features.chat import register_chat_features
from app.bot.features.persona import register_persona_features
from app.bot.features.tools import register_tool_features


def register_features(bot: Dispatcher):
    register_generate_features(bot)
    register_ask_features(bot)
    register_main_menu_features(bot)
    register_chat_features(bot)
    register_persona_features(bot)
    register_tool_features(bot)
    register_global_handler(bot)
