import secrets
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from entities.ai_character import AICharacter


class ChatSessionManager:
    def __init__(self):
        self.sessions: dict[str, dict] = {}

    def create(self, user_id: UUID, character_ids: list[UUID], db: Session) -> str:
        owned = (
            db.query(AICharacter.id)
            .filter(AICharacter.owner_id == user_id, AICharacter.id.in_(character_ids))
            .all()
        )
        if len(owned) != len(character_ids):
            raise HTTPException(status_code=403, detail="Character ownership mismatch")
        session_id = secrets.token_urlsafe(16)
        self.sessions[session_id] = {
            "owner_id": user_id,
            "character_ids": character_ids,
            "connections": set(),
            "messages": [],
        }
        return session_id

    def get(self, session_id: str):
        return self.sessions.get(session_id)

    def discard(self, session_id: str):
        self.sessions.pop(session_id, None)


session_manager = ChatSessionManager()
