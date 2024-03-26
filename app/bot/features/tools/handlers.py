from aiogram import types
from app.bot.bot_state import State
from app.bot.person_list import Persona, PersonaState

from .keyboards import tools_kb
from .texts import tools_text
import time


async def handle_tools_command(message: types.Message):
    try:
        if message.chat.id <= 0:
            return
        return await message.answer(text=tools_text, reply_markup=tools_kb)
    except Exception:
        return await message.answer(text="Something happened, please come back later.")


async def handle_tools_callback(call: types.CallbackQuery):
    try:
        return await call.message.answer(text=tools_text, reply_markup=tools_kb)
    except Exception:
        return await call.message.answer(
            text="Something happened, please come back later."
        )


async def handle_tool_click_callback(call: types.CallbackQuery):
    try:
        tool_name = call.data
        chat_id = str(call.message.chat.id)
        try:
            tool: Persona = PersonaState[tool_name]

            State[chat_id].update(
                {
                    "last_chat": tool_name,
                    "last_request": int(time.time()),
                    "session_id": None,
                    "history": [],
                }
            )

            await call.message.answer_sticker(tool.get_initial_sticker())
            return await call.message.answer(
                tool.get_greeting_text(call.message.chat.username)
            )

        except Exception:
            return await call.message.answer(
                "You need a premium account to have an access to this persona"
            )

    except Exception:
        return await call.message.answer(
            text="Something happened, please come back later."
        )
