from fastapi import FastAPI
from auth.controllers import router as auth_router
from users.controllers import router as users_router
from chat.controllers import router as chat_router
from chat.websocket import ws_router as chat_ws_router


def register_routes(app: FastAPI):

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(chat_router)
    app.include_router(chat_ws_router)
