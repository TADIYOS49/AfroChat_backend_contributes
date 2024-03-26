from typing import List
from aiogram.types import BotCommand


BOT_COMMANDS: List[BotCommand] = [
    BotCommand("start", "Open Menu"),
    BotCommand("help", "Get Help"),
    BotCommand("ask", "Ask me anything"),
    BotCommand("chat", "Start a conversation with Chat-GPT"),
    BotCommand("personas", "Select preferable persona to chat with"),
    BotCommand("tools", "List all our tools"),
    # BotCommand("register", "Register your phone number for the web App"),
    # BotCommand("generate", "Generate image to your heart's desire"),
]

BOT_COMMANDS_GROUP: List[BotCommand] = [
    BotCommand("ask", "Ask me anything including group messages"),
    BotCommand("generate", "Generate image to your heart's desire"),
]
