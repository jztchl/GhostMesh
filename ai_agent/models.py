from pydantic import BaseModel
from entities.ai_character import AICharacter
from uuid import UUID


class AICharacterRequest(BaseModel):
    name: str
    description: str
    personality_traits: str


class AICharacterResponse(AICharacterRequest):
    id: UUID


class AICharacterListResponse(BaseModel):
    id: UUID
    name: str
