import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.service import CurrentUser
from entities.ai_character import AICharacter

from .models import AICharacterRequest


class AICharacterService:
    def __init__(self, db: Session):
        self.db = db

    def create_ai_character(
        self, request: AICharacterRequest, current_user: CurrentUser
    ):
        try:
            new_ai_character = AICharacter(
                name=request.name,
                description=request.description,
                personality_traits=request.personality_traits,
                owner_id=current_user.get_uuid(),
            )
            self.db.add(new_ai_character)
            self.db.commit()

            return new_ai_character

        except Exception as e:
            logging.error(f"Failed to create AI character: {str(e)}")
            raise

    def get_ai_character(self, ai_character_id: UUID, current_user: CurrentUser):
        try:
            ai_character = (
                self.db.query(AICharacter)
                .filter(
                    AICharacter.id == ai_character_id,
                    AICharacter.owner_id == current_user.get_uuid(),
                )
                .first()
            )
            if not ai_character:
                raise HTTPException(status_code=404, detail="AI character not found")
            return ai_character

        except Exception as e:
            logging.error(f"Failed to get AI character: {str(e)}")
            raise

    def list_ai_characters(self, current_user: CurrentUser):
        try:
            stmt = select(AICharacter.id, AICharacter.name).where(
                AICharacter.owner_id == current_user.get_uuid()
            )
            ai_characters = self.db.execute(stmt).mappings().all()
            return ai_characters
        except Exception as e:
            logging.error(f"Failed to list AI characters: {str(e)}")
            raise
