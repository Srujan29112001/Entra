"""Tests for specialist agents."""

import pytest
from app.agents.finance_agent import FinanceAgent
from app.agents.tax_agent import TaxPolicyAgent
from app.agents.market_agent import MarketStrategyAgent
from app.agents.wealth_agent import PersonalWealthAgent


@pytest.mark.asyncio
async def test_finance_agent_runway_calculation(sample_task):
    """Test finance agent runway calculation."""
    agent = FinanceAgent()
    result = await agent.process(sample_task)

    assert result.agent_type == "finance"
    assert result.data is not None
    assert "runway_months" in result.data
    assert result.data["runway_months"] == 10.0


@pytest.mark.asyncio
async def test_tax_agent_calculation():
    """Test tax agent calculation."""
    from app.models.schemas import AgentTask

    agent = TaxPolicyAgent()
    task = AgentTask(
        task_id="test-tax",
        agent_type="tax",
        question="Calculate my tax liability",
        context={
            "company_data": {
                "annual_profit": 100000,
                "country": "US",
                "founder_salary": 80000,
            }
        },
        user_id="user-123",
        company_id="comp-123",
    )

    result = await agent.process(task)

    assert result.agent_type == "tax"
    assert result.data is not None
    assert "corporate_tax" in result.data


@pytest.mark.asyncio
async def test_market_agent():
    """Test market strategy agent."""
    from app.models.schemas import AgentTask

    agent = MarketStrategyAgent()
    task = AgentTask(
        task_id="test-market",
        agent_type="market",
        question="Analyze my market strategy",
        context={
            "company_data": {
                "industry": "SaaS",
                "country": "US",
                "stage": "seed",
            }
        },
        user_id="user-123",
        company_id="comp-123",
    )

    result = await agent.process(task)

    assert result.agent_type == "market"
    assert result.data is not None


@pytest.mark.asyncio
async def test_wealth_agent():
    """Test personal wealth agent."""
    from app.models.schemas import AgentTask

    agent = PersonalWealthAgent()
    task = AgentTask(
        task_id="test-wealth",
        agent_type="wealth",
        question="Optimize my salary",
        context={
            "company_data": {
                "runway_months": 12,
                "monthly_expenses": 10000,
            },
            "personal_data": {
                "monthly_expenses": 5000,
            },
        },
        user_id="user-123",
        company_id="comp-123",
    )

    result = await agent.process(task)

    assert result.agent_type == "wealth"
    assert result.data is not None
    assert "optimal_salary" in result.data
