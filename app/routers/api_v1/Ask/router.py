from uuid import UUID
from fastapi import APIRouter, Depends, Body
from app.routers.api_v1.Ask.schemas import (
    AskFollowUpRequest,
    AskRequest,
    AskResponse,
    Session,
    SessionType,
)
from app.routers.api_v1.Ask.service import (
    ask_follow_up_service,
    ask_service,
    delete_session_service,
    get_ask_messages_service,
    get_pinned_sessions_service,
    get_sessions_service,
    toggle_pin_service,
)
from app.routers.api_v1.Auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.database.database import get_db
from app.routers.api_v1.Auth.dependencies import (
    get_activated_user,
    get_request_number_validated_user,
)
from app.routers.api_v1.Service.schemas import Paginate

ask_router = APIRouter(prefix="/ask", tags=["Ask"])


@ask_router.get("/get_questions", status_code=200)
async def get_questions(
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
):
    questions = [
        "What is consciousness and how does it emerge?",
        "Is there life beyond Earth?",
        "How do our memories work and where are they stored?",
        "What is the nature of time? Is it linear or cyclical?",
        "How do vaccines work to prevent diseases?",
        "What causes deja vu and why do we experience it?",
        "How do animals communicate with each other?",
        "What is the future of artificial intelligence?",
        "What happens inside a black hole?",
        "How do dreams influence our waking life?",
        "What are the limits of human perception?",
        "How do we form habits and how can we break them?",
        "What is the true extent of human potential?",
        "How do cultures evolve and change over time?",
        "What is the purpose of dreams and do they hold any significance?",
        "Can we ever achieve world peace and what would it take?",
        "How do different cultures define and understand beauty?",
        "What causes mental illnesses and how can they be effectively treated?",
        "What are the ethical implications of genetic engineering?",
        "What is the future of space exploration and colonization?",
    ]

    return {"questions": questions}


@ask_router.post("/ask", response_model=AskResponse, status_code=200)
async def ask(
    ask_request: Annotated[AskRequest, Body],
    user: User = Depends(get_request_number_validated_user),
    db_session: AsyncSession = Depends(get_db),
):
    response = await ask_service(ask_request, user, db_session)
    return response


@ask_router.post("/ask_follow_up", response_model=AskResponse, status_code=200)
async def ask_follow_up(
    ask_follow_up_request: Annotated[AskFollowUpRequest, Body],
    user: User = Depends(get_request_number_validated_user),
    db_session: AsyncSession = Depends(get_db),
):
    response = await ask_follow_up_service(ask_follow_up_request, user, db_session)
    return response


@ask_router.get(
    "/get_chat_messages/{ask_session_id}",
    response_model=Paginate[AskResponse],
    status_code=200,
)
async def get_ask_messages(
    ask_session_id: UUID,
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    response = await get_ask_messages_service(
        ask_session_id, user, db_session, offset, limit
    )
    return response


@ask_router.get("/get_sessions/", response_model=Paginate[Session], status_code=200)
async def get_sessions(
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    response = await get_sessions_service(user, db_session, offset, limit)
    return response


@ask_router.put("/toggle_pin/{ask_session_id}", response_model=object, status_code=200)
async def toggle_pin(
    session_id: UUID,
    session_type: SessionType = SessionType.CHAT,
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
):
    response = await toggle_pin_service(session_id, session_type, user, db_session)
    return response


@ask_router.get(
    "/get_pinned_sessions/", response_model=Paginate[Session], status_code=200
)
async def get_pinned_sessions(
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    response = await get_pinned_sessions_service(user, db_session, offset, limit)
    return response


@ask_router.delete("/delete_session/{session_id}", status_code=200)
async def delete_session(
    session_id: UUID,
    session_type: SessionType = SessionType.CHAT,
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
):
    await delete_session_service(session_id, session_type, user, db_session)
    return {"success": True, "message": "Session deleted successfully."}
