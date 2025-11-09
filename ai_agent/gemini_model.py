import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
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

_executor = ThreadPoolExecutor()


def _call_gemini(instruction: str, context: str):
    return client.models.generate_content(
        model="gemini-2.5-flash",
        config=GenerateContentConfig(
            system_instruction=instruction,
            tools=tools,
        ),
        contents=context,
    )


async def get_llm_response(instruction: str, context: str) -> str:
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(_executor, _call_gemini, instruction, context)
    return response.text


async def generate_ai_character_response(
    ai_character_ids: list[UUID], user_message: str, db: Session
) -> dict[str, str]:
    ai_characters = (
        db.query(AICharacter).filter(AICharacter.id.in_(ai_character_ids)).all()
    )

    names: list[str] = []
    tasks: list[asyncio.Task[str]] = []

    for ai_character in ai_characters:
        instruction = (
            f"{BASE_INSTRUCTION}: {ai_character.personality_traits or ''}".strip()
        )
        names.append(ai_character.name)
        tasks.append(get_llm_response(instruction, user_message))

    results = await asyncio.gather(*tasks)
    return dict(zip(names, results))
