from datetime import datetime

import asyncio
import random
from typing import List, Tuple
from uuid import UUID

import aiohttp
from fastapi import BackgroundTasks
from sqlalchemy.exc import SQLAlchemyError
import ujson
from app.routers.api_v1.Image.constants import GOOGLE_GEMINI_API, GROQ_API_KEY
from app.constants import LLMModels
from app.database.database import get_db_context

from app.routers.api_v1.Auth.models import AskTelegram
from app.routers.api_v1.Functional_Tools.constants import functional_tools
from app.routers.api_v1.Functional_Tools.services import handle_tool_call
from app.routers.api_v1.chat.models import MessageFrom, TelegramGroupMessage
from app.routers.api_v1.chat.schemas import ChatCreate
from config import initial_config


async def make_request(
    messages: List[dict[str, str]],
    model: LLMModels,
    tools_to_use: List[str] | None = None,
    max_tokens: int = 2048,
) -> Tuple[str, int, int, int]:
    # Define model URLs and headers in a structured way
    model_urls = {
        # LLMModels.GPT35: "https://api.openai.com/v1/chat/completions",
        LLMModels.GEMINIPRO: f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_GEMINI_API}",
        LLMModels.MISTRAL: "https://api.groq.com/openai/v1/chat/completions",
        LLMModels.LLAMA: "https://api.groq.com/openai/v1/chat/completions",
        LLMModels.GEMMA: "https://api.groq.com/openai/v1/chat/completions",
    }

    model_headers = {
        # LLMModels.GPT35: {
        #     "Authorization": f"Bearer {initial_config.OPENAI_API_KEY}",
        #     "Content-Type": "application/json",
        # },
        LLMModels.GEMINIPRO: {"Content-Type": "application/json"},
        LLMModels.MISTRAL: {"Authorization": "Bearer " + f"{GROQ_API_KEY}"},
        LLMModels.LLAMA: {"Authorization": "Bearer " + f"{GROQ_API_KEY}"},
        LLMModels.GEMMA: {"Authorization": "Bearer " + f"{GROQ_API_KEY}"},
    }

    tools = [functional_tools[tool] for tool in tools_to_use] if tools_to_use else []

    add_prompt = "Remove any self-referential information, such as names or pronouns referring to the speaker, as well as information enclosed in '[]'. Ensure the response is **always in English**, unless instructed otherwise."

    # Build model-specific payload
    model_payload = {
        # LLMModels.GPT35: {
        #     "model": "gpt-3.5-turbo",
        #     "messages": messages,
        #     "temperature": round(
        #         random.uniform(0.2, 1), 1
        #     ),  # FIXME:This is a temporary and inefficient we need to fix this.
        #     "max_tokens": max_tokens,
        #     "tools": tools if tools else None,
        #     "tool_choice": "auto" if tools else None,
        # },
        LLMModels.GEMINIPRO: {
            "contents": [
                {
                    "parts": [
                        {
                            "text": message["content"] + add_prompt
                            if message == messages[0]
                            else message["content"]
                        }
                        for message in messages
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": max_tokens,
            },
        },
        LLMModels.MISTRAL: {
            "model": "mixtral-8x7b-32768",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
        LLMModels.LLAMA: {
            "model": "llama2-70b-4096",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
        LLMModels.GEMMA: {
            "model": "gemma-7b-it",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
    }

    # Define model-specific handler functions
    model_handlers = {
        LLMModels.GEMINIPRO: handle_gemini_pro,
        # LLMModels.GPT35: handle_gpt_3_5_turbo,
        LLMModels.MISTRAL: handle_gpt_3_5_turbo,
        LLMModels.LLAMA: handle_gpt_3_5_turbo,
        LLMModels.GEMMA: handle_gpt_3_5_turbo,
        # Add more models as needed
    }

    # Retrieve model-specific URL, payload, and headers
    url = model_urls[model]
    payload = ujson.dumps(model_payload[model])
    headers = model_headers[model]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    handler_function = model_handlers[model]
                    return await handler_function(data, messages)

                else:
                    raise Exception(
                        f"Request failed with status code {response.status}\
                                error : {await response.text()}",
                    )
    except Exception as e:
        # Handle the exception here other exceptions here
        raise Exception(f"Request failed {str(e)}")


# FIXME Retrieve usagemetadata
async def handle_gemini_pro(data, messages):
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0

    return answer, total_tokens, prompt_tokens, completion_tokens


async def handle_gpt_3_5_turbo(data, messages):
    finish_reason = data["choices"][0]["finish_reason"]

    if finish_reason == "tool_calls":
        messages.append(data["choices"][0]["message"])
        return await handle_tool_call(
            messages, data["choices"][0]["message"]["tool_calls"]
        )

    answer = data["choices"][0]["message"]["content"]
    total_tokens = data["usage"]["total_tokens"]
    prompt_tokens = data["usage"]["prompt_tokens"]
    completion_tokens = data["usage"]["completion_tokens"]

    return answer, total_tokens, prompt_tokens, completion_tokens


async def make_ask_request(
    question: str,
    user_id: UUID,
    system_message: str | None = None,
    group_id: int = 99,  # 99 means it's not from group
):
    messages = [
        {
            "role": "system",
            "content": (
                system_message
                if system_message
                else f"You are a helpful assistant and your name is AfroChat made by A2SV. Today is {str(datetime.utcnow())}"
            ),
        },
        {"role": "user", "content": question},
    ]
    answer, total_tokens, _, _ = await make_request(
        messages,
        # tools_to_use=["search_news"],
        model=LLMModels.MISTRAL,
    )

    async def add_ask():
        async with get_db_context() as db_session:
            await AskTelegram.add_ask_telegram(
                db_session,
                user_id,
                question,
                answer,
                total_tokens,
                group_id,
            )

    asyncio.create_task(add_ask())
    return answer


def format_datetime(time: int):
    return datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M")


async def answer_group_message_question(
    group_id: int,
    group_topic: int,
    question: str,
    user_id: UUID,
):
    async with get_db_context() as db_session:
        prev_message = await TelegramGroupMessage.get_previous_conversations(
            db_session=db_session,
            group_id=group_id,
            group_topic=group_topic,
            limit=initial_config.GROUP_CHAT_MESSAGE_LIMIT,
        )
        prev_cono = ""
        for messages in prev_message:
            prev_cono += f"> {messages.telegram_user.full_name}\n + {format_datetime(messages.created_at)}\n {messages.text}\n\n"
    prompt = f"""
you are a bot that is there to assist people when they ask you a question.
you have access to group members previous conversations so it's based on that context you will answer the questions.
the previous conversation is as follows the following format:
FORMAT:

> User
date
message


Now i will give you the Previous conversation and Question and i want you to return the answer
----------------------

PREVIOUS CONVERSATION:

{prev_cono}

Question:
{question}
"""

    answer = await make_ask_request(
        question=prompt,
        user_id=user_id,
        group_id=group_id,
    )

    # return answer
    return answer


async def make_chat_request(
    question: str,
    user_id: UUID,
    persona_id: UUID,
    session_id: UUID | None,
    tool_or_persona: str,
) -> Tuple[str, UUID]:
    try:
        # prepare a messages array that is list of dicts
        # add the system prompt at the beginning
        ai_response: list[str] = []

        # if session id is none it means it is a new conversation so create a new session and save it

        if session_id is None:
            # telegram_bot_logger.error("creating new chat")
            from app.routers.api_v1.chat.service import create_new_chat

            async with get_db_context() as db_session:
                # create a new Conversation object
                new_chat = ChatCreate(
                    question=question, message_from=MessageFrom.TELEGRAM_BOT
                )
                if tool_or_persona == "persona":
                    new_chat.persona_id = persona_id
                else:
                    new_chat.sub_tool_id = persona_id

                try:
                    chat_response = await create_new_chat(db_session, new_chat, user_id)
                except Exception as e:
                    raise e

                session_id = chat_response.id
                response = [
                    x for x in chat_response.chat_messages if x.role == "assistant"
                ][0]
                ai_response.append(response.message)

        else:
            from app.routers.api_v1.chat.service import ask_question_service

            async with get_db_context() as db_session:
                chat_response = await ask_question_service(
                    db_session=db_session,
                    chat_session_id=session_id,
                    question=question,
                    user_id=user_id,
                    worker=BackgroundTasks(),
                    message_from=MessageFrom.TELEGRAM_BOT,
                    current_model=LLMModels.MISTRAL,
                )

                response = [x for x in chat_response if x.role == "assistant"][0]
                ai_response.append(response.message)
                pass

        return ai_response[0], session_id
    except SQLAlchemyError as e:
        raise e


# API call to generate image
async def generate_image(prompt, quality="standard", n=1):
    api_url = "https://api.openai.com/v1/images/generations"

    params = {
        "model": "dall-e-3",
        "prompt": prompt,
        # "size": size,
        "quality": quality,
        "n": n,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {initial_config.OPENAI_API_KEY}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=params, headers=headers) as response:
            if response.status == 200:
                try:
                    response_json = await response.json()
                    image_url = response_json["data"][0]["url"]
                    return image_url
                except Exception as e:
                    raise e
            else:
                raise Exception("content_policy_violation")
