from logging import Logger
from uuid import UUID
from aiogram import types

from app.bot.api_requests import answer_group_message_question, make_ask_request
from app.bot.features.utils import telegram_get_user_id
from app.database_operations import get_user_id_for_telegram
from .texts import chat_text
from .keyboards import ask_keyboard
import time
from app.bot.bot_state import State
from app.utils.logger import TelegramBotLogger

# create an instance for aiogram logger
aiogram_logger = Logger("aiogram")


async def ask_command_handler(message: types.Message):
    try:
        command = message.text.split(maxsplit=1)
        suggestion = f"or {command[0]}" if command[0] != "/ask" else ""
        # check if the message is empty
        if len(command) < 2:
            await message.reply(
                f"Invalid command please type /ask {suggestion} then your prompt."
            )
            return

        if (
            message.text.strip() == "/ask"
        ):  # this checks will guarentee question is being asked only inside groups
            # save the state only when it's used inside the bot and not groupts
            if message.chat.id <= 0:
                return
            chat_id = str(message.chat.id)
            State[chat_id].update(
                {"last_chat": "ask", "last_request": int(time.time())}
            )
            return await message.answer(text=chat_text, reply_markup=ask_keyboard)

        question = message.text.strip().split(maxsplit=1)[1]
        if len(question) == 1:
            return await message.answer(text="Please ask a question.")

        if message.chat.id > 0:
            # message is from inside a bot and not group
            response = await message.reply(text="Getting your answer please wait...❄️")
            telegram_user_id: UUID = await telegram_get_user_id(
                str(message.from_user.id), message
            )
            answer = await make_ask_request(
                question=message.text, user_id=telegram_user_id
            )
            return await response.edit_text(answer)

        user_id: UUID | None = await get_user_id_for_telegram(str(message.from_user.id))

        if not user_id:
            return await message.answer(
                text="You have to use the bot atleast once inorder to have access to this feature!!"
            )
        # if it's from a group make sure to get the group previous chat
        # get the previous convo from the group

        response = await message.reply(text="Getting your answer please wait...❄️")
        group_id: int = message.chat.id
        group_topic: int = (
            -1 if not message.is_topic_message else message.message_thread_id
        )
        TelegramBotLogger.error(f"{group_id} {group_topic} {question}")

        answer = await answer_group_message_question(
            group_id=group_id,
            group_topic=group_topic,
            question=question,
            user_id=user_id,
        )
        return await response.edit_text(answer)

    except Exception as e:
        TelegramBotLogger.error(e)
        aiogram_logger.critical(e)
        return await message.answer(text="Something happened, please come back later.")


async def handle_ask_callback(call: types.CallbackQuery):
    try:
        # FIXME
        initial_time, current_time = int(call.message.date.timestamp()), int(
            time.time()
        )
        diff = abs(initial_time - current_time)
        diff /= 60

        chat_id = str(call.message.chat.id)
        State[chat_id].update({"last_chat": "ask", "last_request": int(time.time())})
        return await call.message.answer(text=chat_text, reply_markup=ask_keyboard)
    except Exception:
        return await call.message.answer(
            text="Something happened, please come back later."
        )
