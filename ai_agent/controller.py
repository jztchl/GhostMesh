from fastapi import APIRouter
from sqlalchemy.orm import Session
from uuid import UUID
from .gemini import generate_ai_character_response

router = APIRouter(prefix="/ai-character")


@router.post("/create-character")
async def create_ai_character():
    pass


@router.get("/get-character")
async def get_ai_character():
    pass


@router.delete("/delete-character")
async def delete_ai_character():
    pass


@router.put("/update-character")
async def update_ai_character():
    pass
