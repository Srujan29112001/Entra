"""Personal Wealth & Salary Optimization Agent."""

from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse
from app.tools.wealth_calculators import (
    optimize_founder_salary,
    calculate_equity_value,
    project_wealth_accumulation,
)


class PersonalWealthAgent(BaseAgent):
    """
    Personal Wealth & Salary Specialist Agent.

    Responsibilities:
    - Founder salary optimization
    - Personal tax planning
    - Equity structuring and ESOP
    - Wealth accumulation strategy
    - Exit planning
    - Work-life balance considerations
    """

    @property
    def agent_type(self) -> str:
        return "wealth"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Personal Wealth advisor for entrepreneurs and founders.

Your expertise includes:
- Founder compensation structuring
- Personal financial planning
- Equity vs salary trade-offs
- ESOP and stock option planning
- Personal tax optimization
- Wealth accumulation strategies
- Exit planning and liquidity events
- Risk management and insurance

When answering questions:
1. Balance company needs with personal financial security
2. Consider runway impact of salary decisions
3. Explain equity value and vesting schedules
4. Address personal tax implications
5. Recommend emergency fund levels
6. Discuss risk and diversification
7. Plan for both success and failure scenarios

Be practical, empathetic, and realistic. Help founders make sustainable decisions."""

    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process a personal wealth/salary task.

        Steps:
        1. Get company financials and runway
        2. Get founder's personal situation
        3. Calculate optimal salary
        4. Project wealth scenarios
        5. Generate recommendations
        """
        # Get company and personal data
        company_data = task.context.get("company_data", {})
        personal_data = task.context.get("personal_data", {})

        # Run wealth analysis
        analysis = await self._run_wealth_analysis(company_data, personal_data)

        # Generate recommendations
        insights = await self._call_llm(
            prompt=task.question,
            context={
                "company_data": company_data,
                "personal_data": personal_data,
                "analysis": analysis,
            },
        )

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=insights,
            data=analysis,
            confidence=0.80,
            sources=[{"type": "calculation", "details": "Wealth optimization analysis"}],
            warnings=self._identify_warnings(analysis, company_data),
        )

    async def _run_wealth_analysis(
        self, company_data: dict, personal_data: dict
    ) -> dict:
        """Run personal wealth calculations."""
        results = {}

        # Optimal founder salary
        company_runway = company_data.get("runway_months", 12)
        monthly_burn = company_data.get("monthly_expenses", 0)
        personal_expenses = personal_data.get("monthly_expenses", 5000)

        results["optimal_salary"] = optimize_founder_salary(
            company_runway=company_runway,
            company_burn=monthly_burn,
            personal_expenses=personal_expenses,
        )

        # Equity value projection
        equity_percentage = personal_data.get("equity_percentage", 0.25)
        company_valuation = company_data.get("valuation", 10000000)

        results["equity_value"] = calculate_equity_value(
            equity_percentage=equity_percentage,
            company_valuation=company_valuation,
            vesting_months_completed=personal_data.get("vesting_months", 0),
        )

        # Wealth projection
        annual_salary = results["optimal_salary"]["recommended_annual"]
        results["wealth_projection"] = project_wealth_accumulation(
            annual_salary=annual_salary,
            equity_value=results["equity_value"]["vested_value"],
            years=5,
        )

        return results

    def _identify_warnings(self, analysis: dict, company_data: dict) -> list[str]:
        """Identify personal finance warnings."""
        warnings = []

        salary_info = analysis.get("optimal_salary", {})
        if salary_info.get("recommended_annual", 0) < 60000:
            warnings.append("Recommended salary below sustainable level - consider minimum needs")

        runway = company_data.get("runway_months", 12)
        if runway < 6 and salary_info.get("recommended_annual", 0) > 80000:
            warnings.append("High salary relative to short runway - consider reduction")

        equity = analysis.get("equity_value", {})
        if equity.get("concentration_risk", 0) > 0.8:
            warnings.append("High wealth concentration in company equity - diversify when possible")

        return warnings
