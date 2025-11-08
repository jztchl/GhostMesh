from fastapi import APIRouter, Depends
from db.core import DbSession
from auth.service import CurrentUser
from . import models, service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/sessions", response_model=models.ChatSessionResponse)
def create_session(
    payload: models.ChatSessionRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    session_id = service.session_manager.create(
        user_id=current_user.get_uuid(),
        character_ids=payload.character_ids,
        db=db,
    )
    ws_url = f"/ws/chat/{session_id}"
    return models.ChatSessionResponse(session_id=session_id, websocket_url=ws_url)
