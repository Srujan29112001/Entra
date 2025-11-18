"""Orchestrator API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import OrchestratorRequest, OrchestratorResponse
from app.orchestrator.main import OrchestratorService

router = APIRouter()


def get_orchestrator() -> OrchestratorService:
    """Dependency to get orchestrator instance."""
    return OrchestratorService()


@router.post("/process", response_model=OrchestratorResponse)
async def process_task(
    request: OrchestratorRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
):
    """
    Process a task through the multi-agent orchestrator.

    This endpoint handles complex, multi-agent tasks that require
    coordination between specialist agents.
    """
    try:
        result = await orchestrator.process_request(
            user_id=request.user_id,
            company_id=request.company_id,
            question=request.question,
            context=request.context or {},
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a running task."""
    # TODO: Implement task status tracking
    return {"task_id": task_id, "status": "completed"}
