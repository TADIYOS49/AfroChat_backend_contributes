from uuid import UUID
from aiogram import types
import time
from app.routers.api_v1.Auth.service import check_if_it_can_be_merged, merge_accounts
from app.bot.features.menu.keyboards import start_kb, merge_callback_creator
from app.bot.features.menu.texts import start_text
from aiogram import Dispatcher
import logging


aiogram_logger = logging.getLogger("aiogram")


async def start_handler(message: types.Message):
    try:
        if message.chat.id <= 0:
            return
        data = message.text.split(" ")
        aiogram_logger.error(data)
        if len(data) == 1:
            return await message.answer(text=start_text, reply_markup=start_kb)

        # get the user_id
        user_id = data[1]

        await check_if_it_can_be_merged(str(message.chat.id), UUID(user_id))
        # check if the user_id is valid
        return await message.answer(
            text="Do you want to merge your Mobile account with the current Telegram account? Please click on the button below in less than 1 minute",
            reply_markup=merge_callback_creator(user_id),
        )
    except Exception as e:
        aiogram_logger.error(e)
        return await message.answer(text=start_text, reply_markup=start_kb)


async def handle_mege_callback(call: types.CallbackQuery):
    try:
        # expiration time for this callback is less than 1 minute
        initial_time, current_time = int(call.message.date.timestamp()), int(
            time.time()
        )
        diff = abs(initial_time - current_time)
        diff /= 60
        if diff > 1:
            await call.message.delete()
            return await call.message.answer(
                text="This link has expired, please make sure to send the command back again."
            )
        data = call.data.split(":")
        if len(data) != 2:
            raise Exception("Invalid data")
        user_id = data[1]
        if user_id == "None":
            await call.message.delete()
            return await call.message.answer(text=start_text, reply_markup=start_kb)
        telegram_id = str(call.message.chat.id)
        # call the service here merge_accounts(user_id, telegram_id)
        """
        Logics:
            - if the user_id doesn't exitst then just procced to show the start command.
            - if the telegram_id exists and have been merged before then just send the start command.
        """
        await merge_accounts(
            telegram_id,
            call.message.chat.full_name,
            UUID(user_id),
        )

        # add celebration emojis for merging completed features
        return await call.message.answer("merging completed 🎉")
    except Exception as e:
        aiogram_logger.error(e)
        await call.message.delete()
        return await call.message.answer(text=start_text, reply_markup=start_kb)


async def handle_start_callback(call: types.CallbackQuery):
    # FIXME  should i edit the messages
    initial_time, current_time = int(call.message.date.timestamp()), int(time.time())
    diff = abs(initial_time - current_time)
    diff /= 60

    return await call.message.answer(text=start_text, reply_markup=start_kb)

    # return await call.message.edit_text(text=start_text, reply_markup=start_kb)


async def help_command_handler(message: types.Message):
    try:
        return await Dispatcher.get_current().bot.copy_message(
            message.chat.id, "665082331", "5938", caption=""
        )
    except Exception:
        return
