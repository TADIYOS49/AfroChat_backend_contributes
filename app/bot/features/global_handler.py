from uuid import UUID
from app.bot.api_requests import make_ask_request, make_chat_request
from app.bot.bot_state import State
from app.bot.features.utils import telegram_get_user_id
from app.bot.person_list import PersonaState, Persona
from app.bot.features.menu.keyboards import start_kb
from app.bot.features.menu.texts import start_text
from aiogram import asyncio, types, Dispatcher
from app.database.database import get_db_context
from app.routers.api_v1.chat.models import TelegramGroupMessage
from app.utils.logger import TelegramBotLogger


async def handle_global_state(message: types.Message):
    try:
        TelegramBotLogger.critical(message)
        if message.chat.id <= 0:
            telegram_id: int = message.from_user.id
            group_id: int = message.chat.id
            group_name: str = message.chat.title
            group_topic: int = (
                -1 if not message.is_topic_message else message.message_thread_id
            )
            created_at: int = int(message.date.timestamp())
            text = message.text
            TelegramBotLogger.error(
                f"telegram_id: {telegram_id}, group_id: {group_id}, group_name: {group_name}, group_topic: {group_topic}, created_time: {created_at}"
            )

            async def add_group_message():
                async with get_db_context() as db_session:
                    await TelegramGroupMessage.add_new_group_message(
                        db_session=db_session,
                        telegram_id=telegram_id,
                        group_id=group_id,
                        group_name=group_name,
                        group_topic=group_topic,
                        created_at=created_at,
                        text=text,
                    )

            asyncio.create_task(add_group_message())
            return
        chat_id: str = str(message.chat.id)
        last_chat: str = State[chat_id].get("last_chat", None)
        if not last_chat:
            return await message.answer(text=start_text, reply_markup=start_kb)

        # store the USER_ID locally on dictionary to avoid further requests
        user_id: UUID = await telegram_get_user_id(chat_id, message)

        match last_chat:
            case "ask":
                response = await message.reply(
                    text="Getting your answer please wait...❄️"
                )
                answer = await make_ask_request(question=message.text, user_id=user_id)
                return await response.edit_text(answer)

            case "afro_chat":
                response = await message.answer(text="chat feature❄️")
                pass

            case last_chat if last_chat.startswith("persona") or last_chat.startswith(
                "tool"
            ):
                persona: Persona = PersonaState[last_chat]
                session_id: UUID = State[chat_id].get("session_id")

                sticker_response = await message.answer_sticker(
                    persona.get_intermediate_sticker()
                )
                text_response = await message.reply(persona.get_intermediate_answers())

                response, session_id = await make_chat_request(
                    question=message.text,
                    session_id=session_id,
                    user_id=user_id,
                    persona_id=UUID(persona.uuid),
                    tool_or_persona="persona"
                    if last_chat.startswith("persona")
                    else "tool",
                )

                State[chat_id].update({"session_id": session_id})

                await sticker_response.delete()
                await text_response.edit_text(response)
    except Exception as e:
        TelegramBotLogger.error(e)
        return await message.answer(text="Something happened, please come back later.")


def register_global_handler(bot: Dispatcher):
    bot.register_message_handler(handle_global_state)
