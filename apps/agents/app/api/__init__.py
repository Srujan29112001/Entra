"""API routes."""

from fastapi import APIRouter
from app.api import chat, orchestrator, agents

router = APIRouter()

router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(orchestrator.router, prefix="/orchestrator", tags=["orchestrator"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
