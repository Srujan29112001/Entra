"""Chat API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.orchestrator.main import OrchestratorService
from datetime import datetime
import uuid

router = APIRouter()


def get_orchestrator() -> OrchestratorService:
    """Dependency to get orchestrator instance."""
    return OrchestratorService()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
):
    """
    Handle chat messages and route to appropriate agents.

    This endpoint:
    1. Receives a user message
    2. Routes it through the multi-agent orchestrator
    3. Returns the synthesized response
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # Run through orchestrator
        result = await orchestrator.process_request(
            user_id=request.user_id,
            company_id=request.company_id,
            question=request.message,
        )

        response = ChatResponse(
            session_id=session_id,
            message=ChatMessage(
                role="assistant",
                content=result.final_answer,
                timestamp=datetime.utcnow(),
            ),
            sources=result.metadata.get("sources", []),
            metadata=result.metadata,
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    # TODO: Implement chat history retrieval from database
    return {"session_id": session_id, "messages": []}
