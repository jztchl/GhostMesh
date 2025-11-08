# chat/models.py
from pydantic import BaseModel
from uuid import UUID


class ChatSessionRequest(BaseModel):
    character_ids: list[UUID]


class ChatSessionResponse(BaseModel):
    session_id: str
    websocket_url: str
