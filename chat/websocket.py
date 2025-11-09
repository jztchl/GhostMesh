# chat/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from auth.service import verify_token
from exceptions import AuthenticationError
from .service import session_manager
from ai_agent.gemini_model import generate_ai_character_response
from db.core import SessionLocal

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
        chat_session = session_manager.get(session_id)
        if not chat_session or chat_session["owner_id"] != current_user.get_uuid():
            await websocket.close(code=4403)
            return

        await websocket.accept()
        chat_session["connections"].add(websocket)

        try:
            while True:
                payload = await websocket.receive_json()
                msg = payload.get("message")
                if not msg:
                    continue
                chat_session["messages"].append({"user": msg})
                reply = await generate_ai_character_response(
                    chat_session["character_ids"], chat_session["messages"], db
                )
                chat_session["messages"].extend(reply)

                for conn in list(chat_session["connections"]):
                    await conn.send_json(reply)

        except WebSocketDisconnect:
            chat_session["connections"].discard(websocket)
            if not chat_session["connections"]:
                session_manager.discard(session_id)
        except Exception as exc:
            await websocket.send_json({"error": str(exc)})
            await websocket.close()
            session_manager.discard(session_id)
    finally:
        db.close()
