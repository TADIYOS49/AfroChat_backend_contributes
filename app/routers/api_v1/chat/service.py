from io import BytesIO
import uuid
from datetime import datetime
from typing import Annotated, List

from fastapi import BackgroundTasks, Body, HTTPException
from app.routers.api_v1.Image.service import (
    edit_image_with_prompt,
    generate_description_from_image,
)
from app.constants import LLMModels
from app.routers.api_v1.Auth.exceptions import USER_NOT_FOUND
from app.routers.api_v1.Auth.models import User
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import aiohttp

from app.bot.api_requests import make_request
from app.exceptions import ServiceNotAvailableHTTPException
from app.routers.api_v1.Persona.exceptions import PERSONA_NOT_FOUND
from app.routers.api_v1.Persona.models import Persona
from app.routers.api_v1.Service.utils import paginate_response
from app.routers.api_v1.Tools.exceptions import SUB_TOOL_NOT_FOUND
from app.routers.api_v1.Tools.models import SubTool
from app.routers.api_v1.chat.constants import IMAGE_GENERATOR_API, TOKEN_LIMIT
from app.routers.api_v1.chat.exceptions import (
    CHAT_SESSION_NOT_FOUND,
    IMAGE_GENERATION_FAILED,
    NO_INTERENT_CONNECTION,
    UNAUTHORIZED_RESOURCE_ACCESS,
)
from app.routers.api_v1.chat.models import (
    ChatSession,
    ChatMessage,
    ChatSessionOutModel,
    MessageFrom,
    SummarizedChatSessionSnapShot,
)
from app.routers.api_v1.chat.schemas import (
    ChatCreate,
    ChatMessageOutSchema,
    ChatSessionBaseOutSchema,
)
from app.routers.api_v1.chat.utils import conversation_summarizer, get_total_token
import cloudinary
from app.constants import IMAGEModels
from config import initial_config


async def make_api_call(
    messages: List[dict[str, str]],
    model: LLMModels,
    initial_prompt: str = "",
    question: str = "",
    tools_to_use: List[str] = None,
) -> tuple[str, int, int, int]:
    """
    This function makes an API call to the ChatGpt api and returns the response
    :param messages: list of messages to be used for the API call
    :param model:
    :param initial_prompt: initial prompt to be used for the API call
    :param question: question to be used for the API call
    :param tools_to_use: list of tools that can be used for the API call
    :return: tuple of answer, prompt_tokens, completion_tokens, total_tokens
    """

    # attach the initial_prompt to the messages to the beginning
    if initial_prompt:
        messages.insert(
            0,
            {
                "role": "system",
                "content": initial_prompt + "Today is " + str(datetime.now()),
            },
        )

    # check if the question is empty
    if question:
        # add the new question
        messages.append({"role": "user", "content": question})

    # FIXME remove the token checker : why tho ? because users can't send that amount token for one message
    # make_request
    try:
        total_token = get_total_token(messages)
        assert total_token <= 2048
        return await make_request(
            messages=messages, tools_to_use=tools_to_use, model=model
        )
    except Exception as e:
        err = str(e)
        print(err)
        # FIXME: change this to a token limit exception
        raise ServiceNotAvailableHTTPException(str(e))


async def get_chat_session_messages(
    db_session: AsyncSession, chat_session_id: uuid.UUID
) -> list[dict[str, str]]:
    # TODO
    """
    first check the snapshot so with that I can get the last snapshot
    so with that I can get the snapshot
            - timestamp
            - and the summarized text
    - then I would fetch the previous conversations after that datetime
    if that datetime object doesn't exist
        then take the minimum datetime stamp
    """
    get_summarized_query = (
        select(SummarizedChatSessionSnapShot)
        .where(SummarizedChatSessionSnapShot.chat_session_id == chat_session_id)
        .order_by(SummarizedChatSessionSnapShot.timestamp.desc())
        .limit(1)
    )

    result = await db_session.execute(get_summarized_query)
    summarized_instance: SummarizedChatSessionSnapShot | None = (
        result.scalars().one_or_none()
    )

    stmt = (
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == chat_session_id)
        .order_by(ChatMessage.timestamp.asc())
    )
    if summarized_instance:
        stmt = stmt.where(ChatMessage.timestamp > summarized_instance.timestamp)

    result = await db_session.execute(stmt)
    instance: List[ChatMessage] = list(result.scalars().all())

    # extract the role and message as an array of dict
    messages: List[dict[str, str]] = (
        [{"role": "assistant", "content": summarized_instance.summarized_content}]
        if summarized_instance
        else []
    )
    for chat_message in instance:
        messages.append({"role": chat_message.role, "content": chat_message.message})
    return messages


async def create_new_chat(
    db_session: AsyncSession,
    new_chat: ChatCreate,
    user_id: UUID,
):
    # fetch the user
    db_user: User | None = await User.find(db_session=db_session, user_id=user_id)

    if not db_user:
        raise USER_NOT_FOUND

    if new_chat.persona_id:
        db_persona = await Persona.find_by_id(
            db_session=db_session, persona_id=new_chat.persona_id, user=db_user
        )
        if not db_persona:
            raise PERSONA_NOT_FOUND

        answer, prompt_tokens, completion_tokens, total_tokens = await make_api_call(
            model=new_chat.model,
            initial_prompt=db_persona.initial_prompt,
            question=new_chat.question,
            messages=[],
            tools_to_use=db_persona.functional_tools,
        )

        db_chat_session: ChatSession = ChatSession(
            id=uuid.uuid4(),
            first_message=new_chat.question,
            created_at=datetime.utcnow(),
            total_tokens=total_tokens,
            user_id=user_id,
            persona_id=new_chat.persona_id,
        )
        db_session.add(db_chat_session)

        db_session_message_question: ChatMessage = ChatMessage(
            role="user",
            timestamp=datetime.utcnow(),
            message=new_chat.question,
            token_usage=prompt_tokens,
            chat_session_id=db_chat_session.id,
            message_from=new_chat.message_from.value,
        )
        db_session_message_response: ChatMessage = ChatMessage(
            role="assistant",
            timestamp=datetime.utcnow(),
            message=answer,
            token_usage=completion_tokens,
            chat_session_id=db_chat_session.id,
            message_from=new_chat.message_from.value,
        )

        db_session.add_all(
            [db_chat_session, db_session_message_question, db_session_message_response]
        )
        db_chat_session.persona = db_persona
        db_chat_session.chat_messages.append(db_session_message_question)
        db_chat_session.chat_messages.append(db_session_message_response)

        await db_session.commit()
        return db_chat_session

    # if it's a tool
    if new_chat.sub_tool_id is None:
        raise SUB_TOOL_NOT_FOUND

    db_sub_tool: SubTool | None = await SubTool.find_by_id(
        db_session=db_session,
        sub_tool_id=new_chat.sub_tool_id,
    )

    if db_sub_tool:
        if db_sub_tool.sub_tool_name == "Text to Image":
            if new_chat.image_model == IMAGEModels.STABLEDIFFUSION:
                answer = await generate_image_stable_diffusion(
                    user_id=user_id,
                    image_prompt=new_chat.question,
                )
            elif new_chat.image_model == IMAGEModels.DALLE3:
                answer = await generate_image_dall_e(
                    user_id=user_id, prompt=new_chat.question
                )
            total_tokens, prompt_tokens, completion_tokens = 0, 0, 0

        elif db_sub_tool.sub_tool_name == "Describe Image":
            answer = await generate_description_from_image(image_url=new_chat.question)
            total_tokens, prompt_tokens, completion_tokens = 0, 0, 0

        elif db_sub_tool.sub_tool_name == "Edit Image":
            answer = await edit_image(
                user_id=user_id,
                image_url=new_chat.image_url,
                prompt=new_chat.question,
            )
            total_tokens, prompt_tokens, completion_tokens = 0, 0, 0

        else:
            (
                answer,
                prompt_tokens,
                completion_tokens,
                total_tokens,
            ) = await make_api_call(
                model=new_chat.model,
                initial_prompt=db_sub_tool.sub_tool_initial_prompt,
                question=new_chat.question,
                messages=[],
            )

        db_chat_session: ChatSession = ChatSession(
            first_message=new_chat.question,
            created_at=datetime.utcnow(),
            total_tokens=total_tokens,
            user_id=user_id,
            sub_tool_id=db_sub_tool.sub_tool_id,
        )

        db_session_message_image = None
        if new_chat.image_url:
            db_session_message_image: ChatMessage = ChatMessage(
                role="user",
                timestamp=datetime.utcnow(),
                message=new_chat.image_url,
                token_usage=prompt_tokens,
                chat_session_id=db_chat_session.id,
                message_from=new_chat.message_from.value,
            )

        db_session_message_question: ChatMessage = ChatMessage(
            role="user",
            timestamp=datetime.utcnow(),
            message=new_chat.question,
            token_usage=prompt_tokens,
            chat_session_id=db_chat_session.id,
            message_from=new_chat.message_from.value,
            llm_model=new_chat.model.value,
        )
        db_session_message_response: ChatMessage = ChatMessage(
            role="assistant",
            timestamp=datetime.utcnow(),
            message=answer,
            token_usage=completion_tokens,
            chat_session_id=db_chat_session.id,
            message_from=new_chat.message_from.value,
            llm_model=new_chat.model.value,
        )

        sessions_to_add = [db_chat_session]
        if db_session_message_image:
            sessions_to_add.append(db_session_message_image)

        sessions_to_add.extend(
            [db_session_message_question, db_session_message_response]
        )
        db_session.add_all(sessions_to_add)

        db_chat_session.sub_tool = db_sub_tool
        if db_session_message_image:
            db_chat_session.chat_messages.append(db_session_message_image)
        db_chat_session.chat_messages.append(db_session_message_question)
        db_chat_session.chat_messages.append(db_session_message_response)

        await db_session.commit()
        return db_chat_session
    raise SUB_TOOL_NOT_FOUND


async def ask_question_service(
    db_session: AsyncSession,
    chat_session_id: uuid.UUID,
    question: str,
    user_id: uuid.UUID,
    worker: BackgroundTasks,
    message_from: MessageFrom,
    current_model: LLMModels,
    image_model: IMAGEModels,
):
    db_chat_session = await ChatSession.find_by_id(
        db_session=db_session,
        chat_session_id=chat_session_id,
        user_id=user_id,
    )
    if not db_chat_session:
        raise CHAT_SESSION_NOT_FOUND

    is_image_generator = False
    is_image_describer = False
    is_image_editor = False
    # get the initial prompt
    # test on a commit
    initial_prompt = ""
    llm_model: LLMModels = LLMModels.MISTRAL
    messages: list[dict[str, str]] = []

    if db_chat_session.persona:
        if not db_chat_session.persona.is_active:
            raise PERSONA_NOT_FOUND

        initial_prompt = db_chat_session.persona.initial_prompt
        llm_model = current_model
    elif db_chat_session.sub_tool:
        if db_chat_session.sub_tool.is_archived:
            raise SUB_TOOL_NOT_FOUND

        if db_chat_session.sub_tool.sub_tool_name == "Text to Image":
            is_image_generator = True
        if db_chat_session.sub_tool.sub_tool_name == "Describe Image":
            is_image_describer = True
        if db_chat_session.sub_tool.sub_tool_name == "Edit Image":
            is_image_editor = True

        initial_prompt = db_chat_session.sub_tool.sub_tool_initial_prompt
        llm_model = current_model

    if is_image_generator:
        if image_model == IMAGEModels.STABLEDIFFUSION:
            answer = await generate_image_stable_diffusion(
                user_id=user_id, image_prompt=question
            )
        elif image_model == IMAGEModels.DALLE3:
            answer = await generate_image_dall_e(user_id=user_id, prompt=question)

        total_tokens, prompt_tokens, completion_tokens = 0, 0, 0

    elif is_image_describer:
        answer = await generate_description_from_image(image_url=question)
        total_tokens, prompt_tokens, completion_tokens = 0, 0, 0

    elif is_image_editor:
        temp_messages: list[dict[str, str]] = await get_chat_session_messages(
            db_session=db_session, chat_session_id=chat_session_id
        )
        image_url = temp_messages[-1]["content"]

        answer = await edit_image(user_id=user_id, image_url=image_url, prompt=question)
        total_tokens, prompt_tokens, completion_tokens = 0, 0, 0

    else:
        # get the previous messages in the chat session
        temp_messages: list[dict[str, str]] = await get_chat_session_messages(
            db_session=db_session, chat_session_id=chat_session_id
        )
        messages.extend(temp_messages)

        answer, prompt_tokens, completion_tokens, total_tokens = await make_api_call(
            model=llm_model,
            messages=messages,
            initial_prompt=initial_prompt,
            question=question,
            tools_to_use=db_chat_session.persona.functional_tools
            if db_chat_session.persona
            else None,
        )

        messages.append({"role": "assistant", "content": answer})

    # update the chat session
    db_chat_session.updated_at = datetime.utcnow()

    await db_chat_session.save(db_session=db_session)

    # TODO
    # if the current total token is greater than the TOKEN LiMIT ADD A BACKGROUND TASK to delete it

    if total_tokens >= TOKEN_LIMIT:
        worker.add_task(conversation_summarizer, db_session, messages, chat_session_id)
    db_chat_session.total_tokens += total_tokens

    db_session_message_question: ChatMessage = ChatMessage(
        role="user",
        timestamp=datetime.utcnow(),
        message=question,
        token_usage=prompt_tokens,
        chat_session_id=db_chat_session.id,
        message_from=message_from.value,
    )
    db_session_message_response: ChatMessage = ChatMessage(
        role="assistant",
        timestamp=datetime.utcnow(),
        message=answer,
        token_usage=completion_tokens,
        chat_session_id=db_chat_session.id,
        message_from=message_from.value,
    )

    db_session.add_all(
        [db_chat_session, db_session_message_question, db_session_message_response]
    )

    await db_session.commit()

    return [db_session_message_question, db_session_message_response]


async def find_by_user_id(
    db_session: AsyncSession, user_id: UUID, limit: int = 10, offset: int = 0
):
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.persona), selectinload(ChatSession.sub_tool))
        .order_by(ChatSession.updated_at.desc())
    )
    return await paginate_response(
        statement=stmt,
        db_session=db_session,
        model=ChatSessionBaseOutSchema,
        offset=offset,
        limit=limit,
        sorting_attribute=ChatSession.updated_at.desc(),
        transformer=lambda rows: [
            ChatSessionBaseOutSchema.model_validate(
                ChatSessionOutModel(chat_session=chat_session),
                from_attributes=True,
            )
            for chat_session in rows
        ],
        to_orm=True,
    )


async def check_chat_session_owner(
    db_session: AsyncSession, chat_session_id: uuid.UUID, user_id: UUID
):
    stmt = (
        select(ChatSession)
        .where(ChatSession.id == chat_session_id, ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.persona), selectinload(ChatSession.sub_tool))
    )
    result = await db_session.execute(stmt)
    instance: ChatSession | None = result.scalars().one_or_none()
    if not instance:
        raise UNAUTHORIZED_RESOURCE_ACCESS
    return instance


async def get_all_messages_for_chat_session(
    db_session: AsyncSession,
    chat_session_id: uuid.UUID,
    limit: int = 10,
    offset: int = 0,
):
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == chat_session_id)
        .order_by(ChatMessage.timestamp.desc())
    )

    return await paginate_response(
        statement=stmt,
        db_session=db_session,
        model=ChatMessageOutSchema,
        offset=offset,
        limit=limit,
        sorting_attribute=ChatMessage.timestamp.desc(),
        transformer=lambda rows: list(
            reversed([chat_message for chat_message in rows])
        ),
        to_orm=True,
    )


async def get_pinned_chat_session_service(db_session: AsyncSession, user_id: UUID):
    stmt = (
        select(ChatSession)
        .where((ChatSession.user_id == user_id) & (ChatSession.is_pinned))
        .options(selectinload(ChatSession.persona), selectinload(ChatSession.sub_tool))
        .order_by(ChatSession.created_at.desc())
    )

    return await paginate_response(
        statement=stmt,
        db_session=db_session,
        model=ChatSessionBaseOutSchema,
        offset=0,
        limit=10,
        transformer=lambda rows: [
            ChatSessionBaseOutSchema.model_validate(
                ChatSessionOutModel(chat_session=chat_session),
                from_attributes=True,
            )
            for chat_session in rows
        ],
        to_orm=True,
    )


# FIXME: do both queries in one db session change the person name to AfroChat
async def get_session_id(user: User, db_session: AsyncSession, question: str) -> UUID:
    # Get persona id
    stmt_persona = select(Persona).where(Persona.full_name == "AfroChat").limit(1)

    result_persona = await db_session.execute(statement=stmt_persona)
    persona_instance: Persona | None = result_persona.scalars().one_or_none()

    if not persona_instance:
        raise PERSONA_NOT_FOUND

    # afrochat id
    persona_id = persona_instance.id

    stmt_chat_session = (
        select(ChatSession)
        .where(ChatSession.persona_id == persona_id, ChatSession.user_id == user.id)
        .limit(1)
    )

    result_chat_session_id = await db_session.execute(statement=stmt_chat_session)
    chat_session_instance: ChatSession | None = (
        result_chat_session_id.scalars().one_or_none()
    )

    if not chat_session_instance:
        new_chat = ChatCreate(question=question, persona_id=persona_id)

        chat_session: ChatSession = await create_new_chat(
            db_session=db_session,
            user_id=user.id,
            new_chat=new_chat,
        )
        return chat_session.id

    return chat_session_instance.id


async def generate_image_stable_diffusion(
    user_id: UUID,
    image_prompt: Annotated[str, Body()],
):
    img = await generate_image_from_description(image_prompt=image_prompt)

    timestamp = datetime.utcnow()
    unique_filename = f"{str(user_id)}_{timestamp}"
    public_id = f"generated_images/{unique_filename}"

    # Upload the generated image to Cloudinary with the specified public_id
    cloudinary_url = upload_image_to_cloudinary(img, public_id)
    return cloudinary_url


async def generate_image_dall_e(
    user_id: UUID,
    prompt: str,
    quality="standard",
    n=1,
):
    image_url = await generate_image_from_description_dall_e(prompt=prompt)

    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to download the image"
                )

            image_bytes = await response.read()

    img = BytesIO(image_bytes)

    timestamp = datetime.utcnow()
    unique_filename = f"{str(user_id)}_{timestamp}"
    public_id = f"generated_images/{unique_filename}"

    # Upload the generated image to Cloudinary with the specified public_id
    cloudinary_url = upload_image_to_cloudinary(img, public_id)
    return cloudinary_url


# API call to generate image
async def generate_image_from_description_dall_e(prompt, quality="standard", n=1):
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


async def generate_image_from_description(image_prompt: Annotated[str, Body()]):
    # modelMap = {
    #     "model-b": "CompVis/stable-diffusion-v1-4",
    #     "model-a": "stabilityai/stable-diffusion-xl-base-1.0",
    # }

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {IMAGE_GENERATOR_API}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                API_URL, headers=headers, json=image_prompt
            ) as response:
                if response.status != 200:
                    raise IMAGE_GENERATION_FAILED

                image_bytes = await response.read()
                img = BytesIO(image_bytes)
                return img
        except:
            raise NO_INTERENT_CONNECTION

        finally:
            await session.close()


async def edit_image(
    user_id: UUID,
    image_url: str,
    prompt: str,
):
    img = await edit_image_with_prompt(image_url=image_url, prompt=prompt)

    timestamp = datetime.utcnow()
    unique_filename = f"{str(user_id)}_{timestamp}"
    public_id = f"generated_images/{unique_filename}"

    # Upload the generated image to Cloudinary with the specified public_id
    cloudinary_url = upload_image_to_cloudinary(img, public_id)
    return cloudinary_url


def upload_image_to_cloudinary(image_path, public_id):
    # Upload the image to Cloudinary with the specified public_id
    upload_result = cloudinary.uploader.upload(image_path, public_id=public_id)
    cloudinary_url = upload_result["secure_url"]

    return cloudinary_url
