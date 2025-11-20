import asyncio
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

from fastapi import WebSocket
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GenerateImagesConfig,
    GoogleSearchRetrieval,
)
from sqlalchemy.orm import Session

from chat.service import session_manager
from config import settings
from entities.ai_character import AICharacter

client = genai.Client(api_key=settings.GEMINI_API_KEY)
BASE_INSTRUCTION_P1 = "You are"
BASE_INSTRUCTION_P2 = "Mimic the following personality traits and answer the last message to the user only message no need of behavior, you can also chat with others characters.personality trait:"
BASE_INSTRUCTION_P3 = "If you want to skip the conversation reply simply with a '.'"

# TODO : make useful tools that can be integrated with the AI agent
# def tool1():
#     """A sample function that does something."""
#     print("tool1 called")
#     return "tool1 executed successfully"

# def tool2():
#     """Another sample function."""
#     print("tool2 called")
#     return "tool2 executed successfully"

# tool1_schema = {
#     "name": "tool1",
#     "description": "A sample function that does something.",
#     "parameters": {"type": "OBJECT", "properties": {}}
# }

# tool2_schema = {
#     "name": "tool2",
#     "description": "Another sample function.",
#     "parameters": {"type": "OBJECT", "properties": {}}
# }

# combined_tools = Tool(
#     function_declarations=[tool1_schema, tool2_schema],
#     google_search_retrieval=GoogleSearchRetrieval()
# )

# tools = [combined_tools]

tools = [GoogleSearchRetrieval()]


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


async def get_llm_response(
    instruction: str,
    context: str,
    ai_character_name: str,
    websocket: WebSocket,
    session_id: str,
) -> str:
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(_executor, _call_gemini, instruction, context)
    payload = {"name": ai_character_name, "message": response.text}
    await websocket.send_json(payload)
    session_manager.add_message(session_id, payload)


async def generate_ai_character_response(
    ai_character_ids: list[UUID],
    user_message: list[dict[str, str]],
    db: Session,
    websocket: WebSocket,
    session_id: str,
) -> list[dict[str, str]]:
    ai_characters = (
        db.query(AICharacter).filter(AICharacter.id.in_(ai_character_ids)).all()
    )

    for ai_character in ai_characters:
        instruction = f"{BASE_INSTRUCTION_P1}:{ai_character.name} and {BASE_INSTRUCTION_P2}: {ai_character.personality_traits or ''} {BASE_INSTRUCTION_P3}".strip()
        asyncio.create_task(
            get_llm_response(
                instruction, str(user_message), ai_character.name, websocket, session_id
            )
        )


def generate_image(description: str) -> str:
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=description,
        config=GenerateImagesConfig(
            number_of_images=1,
            image_size="1K",
        ),
    )

    os.makedirs("generated_images", exist_ok=True)

    filename = f"{uuid.uuid4()}.png"
    file_path = os.path.join("generated_images", filename)
    response.generated_images[0].image.save(file_path)
    return file_path
