"""Agents API endpoints."""

from fastapi import APIRouter, HTTPException
from app.models.schemas import AgentTask, AgentResponse
from typing import Literal

router = APIRouter()


@router.post("/invoke/{agent_type}", response_model=AgentResponse)
async def invoke_agent(
    agent_type: Literal["finance", "tax", "market", "legal", "wealth"],
    task: AgentTask,
):
    """
    Directly invoke a specific specialist agent.

    This is useful for testing individual agents or when you know
    exactly which agent you need.
    """
    try:
        # Import agent dynamically
        if agent_type == "finance":
            from app.agents.finance_agent import FinanceAgent
            agent = FinanceAgent()
        elif agent_type == "tax":
            from app.agents.tax_agent import TaxPolicyAgent
            agent = TaxPolicyAgent()
        elif agent_type == "market":
            from app.agents.market_agent import MarketStrategyAgent
            agent = MarketStrategyAgent()
        elif agent_type == "legal":
            from app.agents.legal_agent import LegalAgent
            agent = LegalAgent()
        elif agent_type == "wealth":
            from app.agents.wealth_agent import PersonalWealthAgent
            agent = PersonalWealthAgent()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

        result = await agent.process(task)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invoking agent: {str(e)}")


@router.get("/list")
async def list_agents():
    """List all available specialist agents."""
    return {
        "agents": [
            {
                "type": "finance",
                "name": "Finance & Fund Management Agent",
                "capabilities": [
                    "Runway calculations",
                    "Financial projections",
                    "Unit economics",
                    "Funding strategy",
                ],
            },
            {
                "type": "tax",
                "name": "Tax & Policy Agent",
                "capabilities": [
                    "Tax optimization",
                    "Multi-jurisdiction compliance",
                    "Policy incentives",
                    "Salary vs dividend planning",
                ],
            },
            {
                "type": "market",
                "name": "Market & Strategy Agent",
                "capabilities": [
                    "Go-to-market planning",
                    "Distribution strategy",
                    "SWOT analysis",
                    "Competitive positioning",
                ],
            },
            {
                "type": "legal",
                "name": "Legal & Compliance Agent",
                "capabilities": [
                    "Contract analysis",
                    "Risk identification",
                    "Compliance guidance",
                    "Document processing",
                ],
            },
            {
                "type": "wealth",
                "name": "Personal Wealth Agent",
                "capabilities": [
                    "Personal tax planning",
                    "Salary optimization",
                    "Equity structuring",
                    "Wealth accumulation",
                ],
            },
        ]
    }
