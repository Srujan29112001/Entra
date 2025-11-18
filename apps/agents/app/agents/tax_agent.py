"""Tax & Policy Agent with RAG capabilities."""

from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse
from app.tools.tax_calculators import (
    calculate_corporate_tax,
    calculate_personal_tax,
    optimize_salary_dividend_split,
)


class TaxPolicyAgent(BaseAgent):
    """
    Tax & Policy Specialist Agent.

    Responsibilities:
    - Multi-jurisdiction tax calculations
    - Tax optimization strategies
    - Policy incentive identification
    - Salary vs dividend structuring
    - Compliance guidance
    - Tax law interpretation via RAG
    """

    @property
    def agent_type(self) -> str:
        return "tax"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Tax & Policy advisor for entrepreneurs and startups.

Your expertise includes:
- Corporate and personal tax optimization
- Multi-jurisdiction tax compliance
- Tax law interpretation and application
- Salary vs dividend structuring
- Government incentives and startup schemes
- R&D tax credits
- International tax planning
- GST/VAT compliance

When answering questions:
1. Consider the specific jurisdiction and legal form
2. Provide concrete calculations with assumptions clearly stated
3. Highlight applicable tax incentives and schemes
4. Explain salary vs dividend trade-offs
5. Flag compliance requirements and deadlines
6. Recommend tax-efficient structures
7. Always note: "This is general guidance - consult a tax professional"

Be precise, compliant, and conservative in recommendations. Cite tax laws when applicable."""

    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process a tax-related task.

        Steps:
        1. Retrieve relevant tax laws and policies via RAG
        2. Extract company details (country, legal form, income)
        3. Perform tax calculations
        4. Generate optimization recommendations
        """
        # Retrieve relevant tax laws and policies
        tax_context = await self._retrieve_context(
            query=task.question,
            company_id=task.company_id,
            top_k=5,
        )

        # Get company data
        company_data = task.context.get("company_data", {})
        country = company_data.get("country", "US")
        legal_form = company_data.get("legal_form", "llc")

        # Perform tax calculations
        calculations = await self._run_tax_analysis(company_data, country)

        # Generate recommendations
        insights = await self._call_llm(
            prompt=task.question,
            context={
                "company_data": company_data,
                "tax_laws": [doc.get("content", "") for doc in tax_context],
                "calculations": calculations,
            },
        )

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=insights + "\n\n⚠️ Disclaimer: This is general guidance. Please consult a qualified tax professional for your specific situation.",
            data=calculations,
            confidence=0.80,
            sources=tax_context,
            warnings=self._identify_warnings(calculations, country),
        )

    async def _run_tax_analysis(self, company_data: dict, country: str) -> dict:
        """Run tax calculations."""
        results = {}

        # Corporate tax
        corporate_income = company_data.get("annual_profit", 0)
        if corporate_income:
            results["corporate_tax"] = calculate_corporate_tax(
                income=corporate_income, country=country
            )

        # Personal tax for founder
        founder_salary = company_data.get("founder_salary", 0)
        if founder_salary:
            results["personal_tax"] = calculate_personal_tax(
                income=founder_salary, country=country
            )

        # Salary vs dividend optimization
        total_withdrawal = company_data.get("total_founder_compensation", 100000)
        if total_withdrawal:
            results["optimal_split"] = optimize_salary_dividend_split(
                total_amount=total_withdrawal, country=country
            )

        return results

    def _identify_warnings(self, calculations: dict, country: str) -> list[str]:
        """Identify tax-related warnings."""
        warnings = []

        corp_tax = calculations.get("corporate_tax", {})
        if corp_tax.get("effective_rate", 0) > 0.30:
            warnings.append("High effective tax rate - explore tax incentives")

        personal_tax = calculations.get("personal_tax", {})
        if personal_tax.get("bracket") == "highest":
            warnings.append("Top tax bracket - consider tax-deferred strategies")

        if country == "IN":
            warnings.append("Remember: GST compliance required for revenue > 20L")

        return warnings
