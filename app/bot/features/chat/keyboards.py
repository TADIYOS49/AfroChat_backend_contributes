from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

chat_keyboard = InlineKeyboardMarkup(row_width=2)
chat_keyboard.row(
    InlineKeyboardButton(text="🔙 Go Back to Main Menu", callback_data="start")
)
