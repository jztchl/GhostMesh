from collections import defaultdict
from google import genai
from google.auth import default
from google.genai.types import GenerateContentConfig
import os
from dotenv import load_dotenv

from entities.ai_character import AICharacter
from uuid import UUID
from sqlalchemy.orm import Session

load_dotenv()
client = genai.Client()

BASE_INSTRUCTION = "Mimic the following personality traits and answer the last message"


def tool1():
    pass


def tool2():
    pass


tools = [
    {"google_search": {}}
    # {"function_declarations": [tool1, tool2]},
]


async def get_llm_response(instruction: str, context: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=GenerateContentConfig(
            system_instruction=instruction,
            tools=tools,
        ),
        contents=context,
    )
    return response.text


async def generate_ai_character_response(
    ai_character_ids: list[UUID], user_message: str, db: Session
):
    response = defaultdict(str)
    ai_characters = (
        db.query(AICharacter).filter(AICharacter.id.in_(ai_character_ids)).all()
    )
    for ai_character in ai_characters:
        instruction = ai_character.personality_traits
        response[ai_character.name] = await get_llm_response(
            BASE_INSTRUCTION + instruction, user_message
        )
    return response
