from uuid import UUID

from fastapi import APIRouter

from auth.service import CurrentUser
from db.core import DbSession

from .models import AICharacterListResponse, AICharacterRequest, AICharacterResponse
from .service import AICharacterService

router = APIRouter(prefix="/ai-character")


@router.post("/create-character", response_model=AICharacterResponse)
async def create_ai_character(
    request: AICharacterRequest, current_user: CurrentUser, db: DbSession
):
    service = AICharacterService(db)
    return service.create_ai_character(request, current_user)


@router.get("/get-character/{ai_character_id}", response_model=AICharacterResponse)
async def get_ai_character(
    ai_character_id: UUID, current_user: CurrentUser, db: DbSession
):
    service = AICharacterService(db)
    return service.get_ai_character(ai_character_id, current_user)


@router.get("/list-character", response_model=list[AICharacterListResponse])
async def list_ai_characters(current_user: CurrentUser, db: DbSession):
    service = AICharacterService(db)
    return service.list_ai_characters(current_user)


@router.delete("/delete-character")
async def delete_ai_character():
    pass


@router.put("/update-character")
async def update_ai_character():
    pass
