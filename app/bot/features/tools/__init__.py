from aiogram import Dispatcher
from .handlers import (
    handle_tool_click_callback,
    handle_tools_command,
    handle_tools_callback,
)


def register_tool_features(bot: Dispatcher):
    bot.register_callback_query_handler(handle_tools_callback, text="tools")
    bot.register_message_handler(handle_tools_command, commands=["tools"])
    bot.register_callback_query_handler(
        handle_tool_click_callback, lambda c: c.data.startswith("tool")
    )
