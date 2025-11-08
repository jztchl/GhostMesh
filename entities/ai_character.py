from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db.core import Base
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint, CheckConstraint


class AICharacter(Base):
    __tablename__ = "ai_characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    personality_traits = Column(String, nullable=True)
    owner = relationship("User", back_populates="ai_characters")

    __table_args__ = (UniqueConstraint("name", "owner_id", name="_name_owner_uc"),)
    __table_args__ = (
        UniqueConstraint("name", "owner_id", name="_name_owner_uc"),
        CheckConstraint(
            "(SELECT COUNT(*) FROM ai_characters WHERE owner_id = ai_characters.owner_id) < 5",
            name="_owner_character_limit",
        ),
    )

    def __repr__(self):
        return f"<AICharacter(name='{self.name}', description='{self.description}')>"
