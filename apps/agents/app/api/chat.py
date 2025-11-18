"""Chat API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.orchestrator.main import OrchestratorService
from app.config import settings
from supabase.client import create_client
from datetime import datetime
import uuid

router = APIRouter()


def get_orchestrator() -> OrchestratorService:
    """Dependency to get orchestrator instance."""
    return OrchestratorService()


async def save_chat_message(
    session_id: str,
    user_id: str,
    company_id: str,
    role: str,
    content: str,
    metadata: dict = None
):
    """
    Save a chat message to the database.

    Args:
        session_id: Chat session identifier
        user_id: User identifier
        company_id: Company identifier
        role: Message role (user or assistant)
        content: Message content
        metadata: Optional metadata
    """
    try:
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        # Ensure session exists
        session_result = supabase.table("chat_sessions") \
            .select("id") \
            .eq("id", session_id) \
            .execute()

        if not session_result.data:
            # Create new session
            supabase.table("chat_sessions").insert({
                "id": session_id,
                "user_id": user_id,
                "company_id": company_id,
                "started_at": datetime.utcnow().isoformat(),
            }).execute()

        # Save message
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }).execute()

    except Exception as e:
        print(f"Error saving chat message: {e}")
        # Don't fail the request if saving fails


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
):
    """
    Handle chat messages and route to appropriate agents.

    This endpoint:
    1. Receives a user message
    2. Persists user message to database
    3. Routes it through the multi-agent orchestrator
    4. Persists assistant response to database
    5. Returns the synthesized response
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # Save user message
        await save_chat_message(
            session_id=session_id,
            user_id=request.user_id,
            company_id=request.company_id,
            role="user",
            content=request.message,
        )

        # Run through orchestrator
        result = await orchestrator.process_request(
            user_id=request.user_id,
            company_id=request.company_id,
            question=request.message,
        )

        # Save assistant message
        await save_chat_message(
            session_id=session_id,
            user_id=request.user_id,
            company_id=request.company_id,
            role="assistant",
            content=result.final_answer,
            metadata=result.metadata,
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
    """
    Get chat history for a session.

    Args:
        session_id: Chat session identifier

    Returns:
        List of messages in chronological order
    """
    try:
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        # Get session
        session_result = supabase.table("chat_sessions") \
            .select("*") \
            .eq("id", session_id) \
            .single() \
            .execute()

        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get messages
        messages_result = supabase.table("chat_messages") \
            .select("role, content, timestamp, metadata") \
            .eq("session_id", session_id) \
            .order("timestamp") \
            .execute()

        messages = messages_result.data if messages_result.data else []

        return {
            "session_id": session_id,
            "session": session_result.data,
            "count": len(messages),
            "messages": messages
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")
