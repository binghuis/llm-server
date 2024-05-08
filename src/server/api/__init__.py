from fastapi import APIRouter

from server.core.config import settings

from .routers import chat_router

routers = APIRouter(prefix=settings.api_prefix)

routers.include_router(chat_router, dependencies=[])
