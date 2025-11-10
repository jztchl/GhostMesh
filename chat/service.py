import json
import secrets
from collections import defaultdict
from uuid import UUID

from fastapi import HTTPException, WebSocket

from db.core import SessionLocal
from db.redis import redis_client
from entities.ai_character import AICharacter


class ChatSessionManager:
    def __init__(self):
        self.redis = redis_client
        self.db = SessionLocal()
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    def create(self, user_id: UUID, character_ids: list[UUID]) -> str:
        owned = (
            self.db.query(AICharacter.id)
            .filter(AICharacter.owner_id == user_id, AICharacter.id.in_(character_ids))
            .all()
        )
        if len(owned) != len(character_ids):
            raise HTTPException(status_code=403, detail="Character ownership mismatch")
        session_id = secrets.token_urlsafe(16)
        self.redis.set(f"session:{session_id}:owner_id", str(user_id))
        if character_ids:
            self.redis.sadd(
                f"session:{session_id}:characters", *[str(cid) for cid in character_ids]
            )
        self.redis.lpush(
            f"session:{session_id}:messages",
            json.dumps({"user": "Begin"}).encode("utf-8"),
        )
        return session_id

    def get_ai_characters(self, session_id: str):
        return [
            UUID(cid.decode("utf-8"))
            for cid in self.redis.smembers(f"session:{session_id}:characters")
        ]

    def get_owner(self, session_id: str):
        return UUID(self.redis.get(f"session:{session_id}:owner_id").decode("utf-8"))

    def add_connection(self, session_id: str, websocket: WebSocket):
        self.active_connections[session_id].append(websocket)

    def remove_connection(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    self.active_connections.pop(session_id)
            except ValueError:
                pass

    def get_connections(self, session_id: str):
        return self.active_connections.get(session_id, [])

    def discard(self, session_id: str):
        pass
        # TODO: add this to api to delete the chat session

    def add_message(self, session_id: str, message: str):
        self.redis.rpush(
            f"session:{session_id}:messages", json.dumps(message).encode("utf-8")
        )

    def get_messages(self, session_id: str):
        msgs = [
            json.loads(m.decode("utf-8"))
            for m in self.redis.lrange(f"session:{session_id}:messages", 0, -1)
        ]
        return msgs


session_manager = ChatSessionManager()
