"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Literal, Any
from datetime import datetime


class UserProfile(BaseModel):
    """User profile data."""

    user_id: str
    country: str
    email: str


class CompanyProfile(BaseModel):
    """Company profile data."""

    company_id: str
    name: str
    country: str
    industry: str
    stage: Literal["idea", "mvp", "seed", "series_a", "series_b", "growth"]
    legal_form: str
    team_size: int | None = None
    monthly_revenue: float | None = None
    monthly_expenses: float | None = None


class ChatMessage(BaseModel):
    """Chat message."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request."""

    user_id: str
    company_id: str
    message: str
    context_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response."""

    session_id: str
    message: ChatMessage
    sources: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


class TaskType(BaseModel):
    """Task classification."""

    type: Literal[
        "finance",
        "tax",
        "market_strategy",
        "legal",
        "personal_wealth",
        "composite",
    ]
    agents_required: list[str]
    complexity: Literal["simple", "medium", "complex"]


class AgentTask(BaseModel):
    """Task for a specialist agent."""

    task_id: str
    agent_type: str
    question: str
    context: dict[str, Any]
    user_id: str
    company_id: str


class AgentResponse(BaseModel):
    """Response from a specialist agent."""

    task_id: str
    agent_type: str
    answer: str
    data: dict[str, Any] | None = None
    confidence: float
    sources: list[dict[str, Any]] | None = None
    warnings: list[str] | None = None


class OrchestratorRequest(BaseModel):
    """Request to the orchestrator."""

    user_id: str
    company_id: str
    question: str
    context: dict[str, Any] | None = None


class OrchestratorResponse(BaseModel):
    """Response from the orchestrator."""

    task_id: str
    final_answer: str
    agent_responses: list[AgentResponse]
    chart_data: dict[str, Any] | None = None
    metadata: dict[str, Any]


class FinancialSnapshot(BaseModel):
    """Financial data snapshot."""

    snapshot_id: str
    company_id: str
    cash_balance: float
    monthly_revenue: float
    monthly_expenses: float
    burn_rate: float
    runway_months: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ScenarioParams(BaseModel):
    """Scenario simulation parameters."""

    scenario_id: str | None = None
    company_id: str
    growth_rate: float = 0.0
    hiring_plan: dict[str, int] | None = None
    price_changes: dict[str, float] | None = None
    funding_amount: float | None = None
    months_to_simulate: int = 12


class ScenarioResult(BaseModel):
    """Scenario simulation result."""

    scenario_id: str
    company_id: str
    params: ScenarioParams
    projections: list[dict[str, Any]]
    summary: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
