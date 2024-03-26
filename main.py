from aiogram import Bot, Dispatcher, types
from app.bot import WEBHOOK_PATH, WEBHOOK_URL, dp, bot, run_bot_with_pooling
from app.bot.bot_commands import BOT_COMMANDS, BOT_COMMANDS_GROUP
from fastapi import Request

from app import create_app, FastApiLogger
from config import initial_config as config
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config import initial_config
import logging


logging.basicConfig(level=logging.ERROR)


def recursive_search(dictionary, target_key) -> dict | str | None:
    if isinstance(dictionary, dict):
        if target_key in dictionary:
            return dictionary[target_key]
        for _, value in dictionary.items():
            result = recursive_search(value, target_key)

            if result is not None:
                return result
    elif isinstance(dictionary, list):
        for item in dictionary:
            result = recursive_search(item, target_key)
            if result is not None:
                return result
    return None


app = create_app(config)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("shutdown")
async def shutdown_event():
    FastApiLogger.info("Shutting down...")


@app.on_event("startup")
async def startup_event():
    # for development make it use pooling
    try:
        FastApiLogger.info("Starting up...")
        await bot.delete_webhook()
        await bot.set_my_commands(
            commands=BOT_COMMANDS, scope=types.BotCommandScopeAllPrivateChats()
        )
        await bot.set_my_commands(
            commands=BOT_COMMANDS_GROUP, scope=types.BotCommandScopeAllGroupChats()
        )
    except Exception as e:
        FastApiLogger.error(e)
        raise e

    # add bot menu
    menu_button = types.MenuButton(
        type="web_app",
        text="AfroChat APP",
        web_app={"url": initial_config.MINI_APP_URL},
    )
    await bot.set_chat_menu_button(None, menu_button)

    if config.CONFIG_TYPE == "development":
        run_bot_with_pooling(dp)
        return
    if config.CONFIG_TYPE == "production":
        # set logger config to ERROR
        try:
            webhook_info = await bot.get_webhook_info()
            FastApiLogger.info(f"webhook_url : {webhook_info.url}")
            if webhook_info.url != WEBHOOK_URL:
                FastApiLogger.info(f"Updating the webhook url to {WEBHOOK_URL}")
                await bot.set_webhook(url=WEBHOOK_URL)
        except Exception as e:
            raise e


GROUP_NAME = "@afrochat_discussion"


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    FastApiLogger.debug(update)
    text = recursive_search(update, "text")
    text = str(text)

    # if "@afro_chat_telegram_bot" in text or "@AFROCHAT_TELEGRAM_BOT_TESTBOT" in text:
    #     return

    # if result:
    #     user_id: int = result.get("id", None)
    #     if user_id:
    #         state: types.ChatMember = await bot.get_chat_member(GROUP_NAME, user_id)
    #         if state.status == "left":
    #             total_users: int = await bot.get_chat_members_count(GROUP_NAME)
    #             if total_users >= 100:
    #                 return await bot.send_message(chat_id=user_id, text="we are at full capacity right now please cameback after a while")

    #             message_text = """Hello! In order to have access to the bot, you need to join our AfroChat Discussion group first.
    #             Please click on this <a href="https://t.me/afrochat_discussion">link</a> or search and join for @afrochat_discussion\
    #                     to join the group and start using the bot.
    #             Thank you😊!"""
    #             return await bot.send_message(chat_id=user_id, text=message_text)

    Dispatcher.set_current(dp)
    Bot.set_current(bot)

    telegram_update = types.Update(**update)
    await dp.process_update(telegram_update)


@app.get("/")
async def home(request: Request):
    logger = request.state.logger
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    return FileResponse("static/index.html")


# use this for debugging only
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
