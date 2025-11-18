"""Streaming support for real-time chat responses."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
import json
import asyncio

from app.orchestrator.main import OrchestratorService

router = APIRouter()


class StreamChatRequest(BaseModel):
    """Request model for streaming chat."""

    user_id: str
    company_id: str
    message: str


async def generate_stream_response(
    orchestrator: OrchestratorService,
    user_id: str,
    company_id: str,
    message: str,
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response from orchestrator.

    Yields:
        Server-Sent Events formatted messages
    """
    try:
        # Send initial event
        yield f"data: {json.dumps({'type': 'start', 'message': 'Processing your request...'})}\n\n"
        await asyncio.sleep(0.1)

        # Send planning status
        yield f"data: {json.dumps({'type': 'status', 'message': 'Analyzing question...'})}\n\n"
        await asyncio.sleep(0.2)

        # Process request
        response = await orchestrator.process_request(
            user_id=user_id,
            company_id=company_id,
            question=message,
            context={},
        )

        # Send agent execution status
        for agent_response in response.agent_responses:
            yield f"data: {json.dumps({'type': 'agent', 'agent_type': agent_response.agent_type, 'status': 'completed'})}\n\n"
            await asyncio.sleep(0.1)

        # Send final answer in chunks for streaming effect
        answer = response.final_answer
        chunk_size = 50  # Characters per chunk
        chunks = [answer[i : i + chunk_size] for i in range(0, len(answer), chunk_size)]

        for chunk in chunks:
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            await asyncio.sleep(0.05)  # Small delay for streaming effect

        # Send completion event
        yield f"data: {json.dumps({'type': 'done', 'metadata': response.metadata})}\n\n"

    except Exception as e:
        # Send error event
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@router.post("/api/v1/chat/stream")
async def stream_chat(request: StreamChatRequest):
    """
    Stream chat responses in real-time.

    Returns Server-Sent Events (SSE) stream.
    """
    orchestrator = OrchestratorService()

    return StreamingResponse(
        generate_stream_response(
            orchestrator,
            request.user_id,
            request.company_id,
            request.message,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        },
    )
