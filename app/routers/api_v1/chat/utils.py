from datetime import datetime
from uuid import UUID

import tiktoken
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.api_requests import make_request
from app.constants import LLMModels
from app.routers.api_v1.chat.models import SummarizedChatSessionSnapShot


async def conversation_summarizer(
    db_session: AsyncSession,
    messages: list[dict[str, str]],
    chat_session_id: UUID,
    message: str = "",
):
    # change the system prompt

    system_prompt = """
    You are a proficient assistant that generates concise summaries of important conversations in chat histories.
    """
    messages[0]["content"] = system_prompt
    messages.append(
        {
            "role": "user",
            "content": """
            Progressively summarize the lines of conversation provided,
            adding onto the previous summary returning a new summary.
            make sure the summery is very short and concise)
            """,
        }
    )

    answer, _, _, total_token = await make_request(messages, model=LLMModels.MISTRAL)
    # perform add operation
    db_summarized_timestamp: SummarizedChatSessionSnapShot = (
        SummarizedChatSessionSnapShot(
            chat_session_id=chat_session_id,
            summarized_content=answer,
            timestamp=datetime.utcnow(),
            token_usage=total_token,
        )
    )
    try:
        await db_summarized_timestamp.save(db_session=db_session)
    except Exception as e:
        print(e)


def get_total_token(
    messages: list[dict[str, str]],
    encoding_name: str = "cl100k_base",
) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    total = 0
    for message in messages:
        total += len(encoding.encode(message["content"]))

    return total
