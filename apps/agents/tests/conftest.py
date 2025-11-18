"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def sample_company_data():
    """Sample company data for testing."""
    return {
        "cash_balance": 100000,
        "monthly_revenue": 20000,
        "monthly_expenses": 15000,
        "cac": 500,
        "ltv": 2000,
        "country": "US",
        "industry": "SaaS",
        "stage": "seed",
    }


@pytest.fixture
def sample_task():
    """Sample agent task for testing."""
    from app.models.schemas import AgentTask

    return AgentTask(
        task_id="test-123",
        agent_type="finance",
        question="Calculate my runway",
        context={"company_data": {"cash_balance": 100000, "monthly_expenses": 10000}},
        user_id="user-123",
        company_id="comp-123",
    )
