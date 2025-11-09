import asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearchRetrieval
from sqlalchemy.orm import Session

from entities.ai_character import AICharacter

load_dotenv()
client = genai.Client()
BASE_INSTRUCTION_P1 = "You are"
BASE_INSTRUCTION_P2 = "Mimic the following personality traits and answer the last message to the user , you can also chat with others too.personality trait:"
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


async def get_llm_response(instruction: str, context: str) -> str:
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(_executor, _call_gemini, instruction, context)
    return response.text


async def generate_ai_character_response(
    ai_character_ids: list[UUID], user_message: list[dict[str, str]], db: Session
) -> list[dict[str, str]]:
    ai_characters = (
        db.query(AICharacter).filter(AICharacter.id.in_(ai_character_ids)).all()
    )

    names: list[str] = []
    tasks: list[asyncio.Task[str]] = []

    for ai_character in ai_characters:
        instruction = f"{BASE_INSTRUCTION_P1}:{ai_character.name} and {BASE_INSTRUCTION_P2}: {ai_character.personality_traits or ''} {BASE_INSTRUCTION_P3}".strip()
        names.append(ai_character.name)
        tasks.append(get_llm_response(instruction, str(user_message)))

    results = await asyncio.gather(*tasks)
    return [{"name": name, "message": result} for name, result in zip(names, results)]
