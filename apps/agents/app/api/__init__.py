"""API routes."""

from fastapi import APIRouter
from app.api import chat, orchestrator, agents, documents

router = APIRouter()

router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(orchestrator.router, prefix="/orchestrator", tags=["orchestrator"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
