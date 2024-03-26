from uuid import UUID

from aiogram import types

from app.bot.bot_state import State
from app.database_operations import get_or_create_user


async def telegram_get_user_id(chat_id: str, message: types.Message) -> UUID:
    user_id: UUID = State[chat_id].get("user_id", None)
    if not user_id:
        user_id = (
            await get_or_create_user(
                telegram_id=chat_id,
                username=f"{message.from_user.username}_{message.from_user.id}",
                full_name=message.from_user.full_name,
            )
        ).id
        State[chat_id].update({"user_id": user_id})
    return user_id
