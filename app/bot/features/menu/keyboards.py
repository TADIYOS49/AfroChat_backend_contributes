from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from config import initial_config


start_kb = InlineKeyboardMarkup(row_width=2)
start_kb.insert(InlineKeyboardButton(text="🗯 Chat GPT", callback_data="chat"))
start_kb.insert(InlineKeyboardButton(text="🗣 AskMe", callback_data="ask"))
start_kb.insert(InlineKeyboardButton(text="🧑‍🎄 Personas 👥", callback_data="personas"))
start_kb.insert(InlineKeyboardButton(text="✍️  Tools ", callback_data="tools"))
# start_kb.insert(InlineKeyboardButton(text='⚙️ Settings', callback_data='setting'))
# start_kb.insert(InlineKeyboardButton(text='🪄 About us', callback_data='about'))

start_kb.row(
    InlineKeyboardButton(
        text="📱 Open App",
        web_app={
            "url": f"{initial_config.MINI_APP_URL}",
        },
    ),
)


merge_cb = CallbackData("merge", "user_id")


def merge_callback_creator(user_id: str):
    merge_kb = InlineKeyboardMarkup(row_width=2)
    merge_kb.insert(
        InlineKeyboardButton(text="👤 Yes", callback_data=merge_cb.new(user_id))
    )
    merge_kb.insert(
        InlineKeyboardButton(text="🚫 No", callback_data=merge_cb.new("None"))
    )
    return merge_kb
