from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

SERVICE_URL = "https://afrochat-bot-telegram-ij7jnmwh2q-zf.a.run.app"
ask_keyboard = InlineKeyboardMarkup(row_width=2)
ask_keyboard.row(
    InlineKeyboardButton(text="🔙 Go Back to Main Menu", callback_data="start"),
)
