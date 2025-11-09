from uuid import UUID

from pydantic import BaseModel


class AICharacterRequest(BaseModel):
    name: str
    description: str
    personality_traits: str


class AICharacterResponse(AICharacterRequest):
    id: UUID


class AICharacterListResponse(BaseModel):
    id: UUID
    name: str
