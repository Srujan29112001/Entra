"""Orchestrator API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import OrchestratorRequest, OrchestratorResponse
from app.orchestrator.main import OrchestratorService
from app.config import settings
from supabase.client import create_client
from datetime import datetime

router = APIRouter()


def get_orchestrator() -> OrchestratorService:
    """Dependency to get orchestrator instance."""
    return OrchestratorService()


async def save_task_status(
    task_id: str,
    user_id: str,
    company_id: str,
    question: str,
    status: str,
    result: dict = None,
    error: str = None
):
    """
    Save or update task status in the database.

    Args:
        task_id: Task identifier
        user_id: User identifier
        company_id: Company identifier
        question: Original question
        status: Task status (pending, processing, completed, failed)
        result: Task result (if completed)
        error: Error message (if failed)
    """
    try:
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        # Check if task exists
        existing = supabase.table("agent_tasks") \
            .select("id") \
            .eq("id", task_id) \
            .execute()

        data = {
            "user_id": user_id,
            "company_id": company_id,
            "question": question,
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }

        if result:
            data["result"] = result
        if error:
            data["error"] = error

        if existing.data:
            # Update existing task
            supabase.table("agent_tasks").update(data).eq("id", task_id).execute()
        else:
            # Insert new task
            data["id"] = task_id
            data["created_at"] = datetime.utcnow().isoformat()
            supabase.table("agent_tasks").insert(data).execute()

    except Exception as e:
        print(f"Error saving task status: {e}")


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
    task_id = None
    try:
        result = await orchestrator.process_request(
            user_id=request.user_id,
            company_id=request.company_id,
            question=request.question,
            context=request.context or {},
        )

        task_id = result.task_id

        # Save completed task status
        await save_task_status(
            task_id=task_id,
            user_id=request.user_id,
            company_id=request.company_id,
            question=request.question,
            status="completed",
            result={
                "answer": result.final_answer,
                "metadata": result.metadata,
            }
        )

        return result

    except Exception as e:
        # Save failed task status
        if task_id:
            await save_task_status(
                task_id=task_id,
                user_id=request.user_id,
                company_id=request.company_id,
                question=request.question,
                status="failed",
                error=str(e),
            )

        raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a running or completed task.

    Args:
        task_id: Task identifier

    Returns:
        Task status and result (if available)
    """
    try:
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        result = supabase.table("agent_tasks") \
            .select("*") \
            .eq("id", task_id) \
            .single() \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Task not found")

        return {
            "task_id": task_id,
            "status": result.data.get("status"),
            "result": result.data.get("result"),
            "error": result.data.get("error"),
            "created_at": result.data.get("created_at"),
            "updated_at": result.data.get("updated_at"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")
