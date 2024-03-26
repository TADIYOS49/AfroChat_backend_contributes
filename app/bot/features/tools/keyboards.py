from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


tools_cb = CallbackData("tool", "name")

tools_kb = InlineKeyboardMarkup(row_width=2)


tools_kb.insert(
    InlineKeyboardButton(
        text="Paraphrasing Prompt",
        callback_data=tools_cb.new("paragrapher"),
    )
)
tools_kb.insert(
    InlineKeyboardButton(
        text="Essay Expander or Summerizer",
        callback_data=tools_cb.new("essay"),
    )
)
tools_kb.insert(
    InlineKeyboardButton(
        text="Targeted Resume",
        callback_data=tools_cb.new("resume"),
    )
)

tools_kb.insert(
    InlineKeyboardButton(
        text="Brainstorming",
        callback_data=tools_cb.new("brainstorm"),
    )
)
