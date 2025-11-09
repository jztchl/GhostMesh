from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db.core import Base
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint


class AICharacter(Base):
    __tablename__ = "ai_characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    personality_traits = Column(String, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="ai_characters")

    __table_args__ = (UniqueConstraint("name", "owner_id", name="_name_owner_uc"),)

    def __repr__(self):
        return f"<AICharacter(name='{self.name}', description='{self.description}')>"
