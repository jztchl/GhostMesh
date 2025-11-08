# chat/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from auth.service import CurrentUser
from .service import session_manager
from .gemini import generate_ai_character_response

ws_router = APIRouter()


@ws_router.websocket("/ws/chat/{session_id}")
async def chat_socket(
    websocket: WebSocket,
    session_id: str,
    current_user: CurrentUser = Depends(),
):
    session = session_manager.get(session_id)
    if not session or session["owner_id"] != current_user.get_uuid():
        await websocket.close(code=4403)
        return

    await websocket.accept()
    session["connections"].add(websocket)

    try:
        while True:
            payload = await websocket.receive_json()
            msg = payload.get("message")
            if not msg:
                continue

            reply = await generate_ai_character_response(
                session["character_ids"], msg, current_user.get_db()
            )

            for conn in list(session["connections"]):
                await conn.send_json(reply)

    except WebSocketDisconnect:
        session["connections"].discard(websocket)
        if not session["connections"]:
            session_manager.discard(session_id)
    except Exception as exc:
        await websocket.send_json({"error": str(exc)})
        await websocket.close()
        session_manager.discard(session_id)
