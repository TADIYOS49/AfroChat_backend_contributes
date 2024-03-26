from aiogram import types
import time
from app.bot.bot_state import State
from .texts import persona_text
from .keyboards import persona_kb
from app.bot.person_list import Persona, PersonaState


async def handle_persona_command(message: types.Message):
    try:
        if message.chat.id <= 0:
            return
        return await message.answer(text=persona_text, reply_markup=persona_kb)
    except Exception:
        return await message.answer(text="Something happened, please come back later.")


async def handle_persona_callback(call: types.CallbackQuery):
    try:
        return await call.message.answer(text=persona_text, reply_markup=persona_kb)
    except Exception:
        return await call.message.answer(
            text="Something happened, please come back later."
        )


async def send_formatted_text(message: types.Message):
    # Sending bold text using HTML
    await message.reply(
        "<b>This is bold text using HTML.</b>", parse_mode=types.ParseMode.HTML
    )

    # Sending italic text using HTML
    await message.reply(
        "<i>This is italic text using HTML.</i>", parse_mode=types.ParseMode.HTML
    )

    # Sending strikethrough text using HTML
    await message.reply(
        "<s>This is strikethrough text using HTML.</s>", parse_mode=types.ParseMode.HTML
    )

    # Sending underline text using HTML
    await message.reply(
        "<u>This is underline text using HTML.</u>", parse_mode=types.ParseMode.HTML
    )

    # Sending a code block using HTML
    code_block = "<pre><code>print('Hello, world!')</code></pre>"
    await message.reply(code_block, parse_mode=types.ParseMode.HTML)

    # Sending a link using HTML
    await message.reply(
        "Check out <a href='https://openai.com'>OpenAI</a>!",
        parse_mode=types.ParseMode.HTML,
    )

    # Mentioning a user using HTML
    await message.reply(
        "Hello, <a href='tg://user?id=USER_ID'>@username</a>!",
        parse_mode=types.ParseMode.HTML,
    )

    # Note that not all formatting options are supported in all clients,
    # and the display may vary across different devices and platforms.


async def handle_persona_click_callback(call: types.CallbackQuery):
    try:
        persona_name = call.data
        chat_id = str(call.message.chat.id)
        try:
            persona: Persona = PersonaState[persona_name]
            # handle your memory code and everything here!!!
            State[chat_id].update(
                {
                    "last_chat": persona_name,
                    "last_request": int(time.time()),
                    "session_id": None,
                    "history": [],
                }
            )
            await call.message.answer_sticker(persona.get_initial_sticker())
            return await call.message.answer(
                persona.get_greeting_text(call.message.chat.username)
            )

        except Exception:
            return await call.message.answer(
                "You need a premium account to have an access to this persona"
            )

        # formatted_text = """*
        # <b>This is bold</b> text using HTML.
        # <i>This is italic</i> text using HTML.
        # <s>This is strikethrough</s> text using HTML.
        # <u>This is underline</u> text using HTML.
        # <code>inline code</code> using HTML.
        # <pre><code>print('Hello, world!')</code></pre> is a code block using HTML.

        # Check out <a href='https://openai.com'>OpenAI</a> for a link using HTML.

        # Hello, <a href='tg://user?id=USER_ID'>@username</a>! is a mention using HTML."""

        # await call.message.reply(formatted_text, parse_mode=types.ParseMode.HTML)
    except Exception:
        return await call.message.answer(
            text="Something happened, please come back later."
        )
