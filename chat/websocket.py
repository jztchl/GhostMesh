# chat/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ai_agent.gemini_model import generate_ai_character_response
from auth.service import verify_token
from db.core import SessionLocal
from exceptions import AuthenticationError

from .service import session_manager

ws_router = APIRouter()


@ws_router.websocket("/ws/chat/{session_id}")
async def chat_socket(
    websocket: WebSocket,
    session_id: str,
):
    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        await websocket.close(code=4401)
        return

    try:
        current_user = verify_token(token)
    except AuthenticationError:
        await websocket.close(code=4401)
        return

    db = SessionLocal()
    try:
        owner = session_manager.get_owner(session_id)
        if not owner or owner != current_user.get_uuid():
            await websocket.close(code=4403)
            return

        await websocket.accept()
        session_manager.add_connection(session_id, websocket)

        try:
            while True:
                payload = await websocket.receive_json()
                msg = payload.get("message")
                if not msg:
                    continue
                session_manager.add_message(session_id, {"user": msg})
                session_manager.refresh_ttl(session_id)
                reply = await generate_ai_character_response(
                    session_manager.get_ai_characters(session_id),
                    session_manager.get_messages(session_id),
                    db,
                )

                for msg in reply:
                    session_manager.add_message(session_id, msg)

                for conn in list(session_manager.get_connections(session_id)):
                    await conn.send_json(reply)

        except WebSocketDisconnect:
            session_manager.remove_connection(session_id, websocket)
            if not session_manager.get_connections(session_id):
                # session_manager.discard(session_id)
                pass
        except Exception as exc:
            await websocket.send_json({"error": str(exc)})
            await websocket.close()
            # session_manager.discard(session_id)
    finally:
        db.close()
