# chat/models.py
from uuid import UUID

from pydantic import BaseModel


class ChatSessionRequest(BaseModel):
    character_ids: list[UUID]


class ChatSessionResponse(BaseModel):
    session_id: str
    websocket_url: str
