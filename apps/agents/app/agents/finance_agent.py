"""Finance & Fund Management Agent."""

from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse
from app.tools.financial_calculators import (
    calculate_runway,
    calculate_burn_rate,
    calculate_unit_economics,
    project_revenue,
)
from app.tools.external_apis import fetch_stock_quote, FinancialDataAPI
import uuid


class FinanceAgent(BaseAgent):
    """
    Finance & Fund Management Specialist Agent.

    Responsibilities:
    - Runway calculations
    - Burn rate analysis
    - Financial projections
    - Unit economics (CAC, LTV)
    - Funding strategy recommendations
    - Scenario modeling
    """

    @property
    def agent_type(self) -> str:
        return "finance"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Finance & Fund Management advisor for startups and entrepreneurs.

Your expertise includes:
- Financial modeling and projections
- Runway and burn rate calculations
- Unit economics optimization (CAC, LTV, payback period)
- Funding strategy (bootstrapping vs. VC, debt vs. equity)
- Cash flow management
- Scenario planning and sensitivity analysis

When answering questions:
1. Always ground recommendations in numbers and data
2. Provide specific calculations and formulas used
3. Consider the company's stage and industry
4. Highlight key metrics and benchmarks
5. Offer actionable recommendations
6. Flag risks and assumptions clearly

Be concise, data-driven, and practical. Use bullet points for clarity."""

    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process a finance-related task.

        Steps:
        1. Retrieve company financial data
        2. Perform relevant calculations
        3. Generate insights and recommendations
        4. Return structured response
        """
        # Get company data (from context or database)
        company_data = task.context.get("company_data", {})

        # Perform calculations
        calculations = await self._run_financial_analysis(company_data, task.question)

        # Generate insights using LLM
        insights = await self._call_llm(
            prompt=task.question,
            context={
                "company_data": company_data,
                "calculations": calculations,
            },
        )

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=insights,
            data=calculations,
            confidence=0.85,
            sources=[{"type": "calculation", "details": "Financial analysis"}],
            warnings=self._identify_warnings(calculations),
        )

    async def _run_financial_analysis(
        self, company_data: dict, question: str
    ) -> dict:
        """Run financial calculations based on the question and company data."""
        results = {}

        # Extract financial metrics
        cash = company_data.get("cash_balance", 0)
        revenue = company_data.get("monthly_revenue", 0)
        expenses = company_data.get("monthly_expenses", 0)

        # Calculate key metrics
        if cash and expenses:
            results["runway_months"] = calculate_runway(cash, expenses)
            results["burn_rate"] = calculate_burn_rate(revenue, expenses)

        # Unit economics
        cac = company_data.get("cac")
        ltv = company_data.get("ltv")
        if cac and ltv:
            results["unit_economics"] = calculate_unit_economics(cac, ltv)

        # Revenue projections
        if revenue:
            growth_rate = company_data.get("growth_rate", 0.1)
            results["projections"] = project_revenue(revenue, growth_rate, months=12)

        return results

    def _identify_warnings(self, calculations: dict) -> list[str]:
        """Identify warnings based on calculations."""
        warnings = []

        runway = calculations.get("runway_months", float("inf"))
        if runway < 3:
            warnings.append("CRITICAL: Less than 3 months runway remaining")
        elif runway < 6:
            warnings.append("WARNING: Less than 6 months runway - start fundraising now")

        burn_rate = calculations.get("burn_rate", 0)
        if burn_rate > 100000:
            warnings.append("High burn rate - review cost structure")

        unit_econ = calculations.get("unit_economics", {})
        if unit_econ.get("ltv_cac_ratio", 0) < 3:
            warnings.append("LTV:CAC ratio below 3 - improve unit economics")

        return warnings
