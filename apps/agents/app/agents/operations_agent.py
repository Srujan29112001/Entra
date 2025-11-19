"""
Operational Advisor Agent.

Handles pricing strategy, supply chain optimization, distribution planning,
team resource planning, and operational efficiency.
"""

from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse
from app.mcp.registry import MCPRegistry
from app.rag.retriever import retriever
from langchain_core.messages import HumanMessage
import math


class OperationsAgent(BaseAgent):
    """
    Operational Advisor Agent.

    Specializes in:
    - Pricing strategy and optimization
    - Supply chain and distribution planning
    - Team resource planning and hiring
    - Salary budgeting and compensation
    - Operational efficiency improvements
    - Process optimization
    """

    def __init__(self):
        """Initialize Operations Agent."""
        super().__init__(
            agent_type="operations",
            capabilities=[
                "pricing_strategy",
                "distribution_planning",
                "team_planning",
                "salary_budgeting",
                "supply_chain",
                "process_optimization",
                "vendor_management",
                "cost_reduction",
            ],
        )

    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process an operations task.

        Args:
            task: Agent task containing the question and context

        Returns:
            AgentResponse with operational recommendations
        """
        # Get MCP client
        mcp_client = await MCPRegistry.get_client("operations_agent")

        # Retrieve relevant knowledge
        relevant_docs = await retriever.retrieve(
            query=task.question,
            company_id=task.company_id,
            document_type="market_research",
            top_k=3,
        )

        # Build context
        context_parts = []

        # Company info
        if task.context:
            company_info = f"""
            Industry: {task.context.get('industry', 'unknown')}
            Country: {task.context.get('country', 'unknown')}
            Stage: {task.context.get('stage', 'unknown')}
            Team Size: {task.context.get('team_size', 0)}
            """
            context_parts.append(company_info)

        # Financial info
        if task.context and 'financials' in task.context:
            fin = task.context['financials']
            financial_info = f"""
            Monthly Revenue: ${fin.get('monthly_revenue', 0):,.2f}
            Monthly Expenses: ${fin.get('monthly_expenses', 0):,.2f}
            Gross Margin: {fin.get('gross_margin', 0)*100:.1f}%
            CAC: ${fin.get('cac', 0):,.2f}
            LTV: ${fin.get('ltv', 0):,.2f}
            """
            context_parts.append(financial_info)

        # RAG context
        if relevant_docs:
            rag_context = "\n\n".join([doc['content'] for doc in relevant_docs])
            context_parts.append(f"Relevant Context:\n{rag_context}")

        full_context = "\n\n".join(context_parts)

        # LLM prompt
        prompt = f"""
        You are an expert Operations advisor specializing in pricing, distribution,
        team planning, and operational efficiency for startups.

        Context:
        {full_context}

        Question: {task.question}

        Provide expert operational advice covering:
        1. Strategic recommendations
        2. Specific action items
        3. Resource allocation suggestions
        4. Cost optimization opportunities
        5. Implementation timeline

        Be specific with numbers, benchmarks, and industry best practices.
        """

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        answer = response.content

        # Extract structured data
        data = await self._extract_operational_data(task, answer)

        # Identify warnings
        warnings = self._identify_warnings(task, data)

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=answer,
            data=data,
            warnings=warnings,
            confidence=0.88,
        )

    async def _extract_operational_data(
        self,
        task: AgentTask,
        answer: str,
    ) -> Dict[str, Any]:
        """Extract structured operational data."""
        data = {}

        if task.context and 'financials' in task.context:
            fin = task.context['financials']
            team_size = task.context.get('team_size', 0)
            monthly_revenue = fin.get('monthly_revenue', 0)
            monthly_expenses = fin.get('monthly_expenses', 0)
            gross_margin = fin.get('gross_margin', 0.7)  # Default 70%
            cac = fin.get('cac', 0)
            ltv = fin.get('ltv', 0)

            # Team planning
            if team_size > 0:
                revenue_per_employee = monthly_revenue / team_size if team_size > 0 else 0
                expense_per_employee = monthly_expenses / team_size if team_size > 0 else 0

                # Industry benchmarks (rough estimates)
                target_revenue_per_employee = 15000  # $15K MRR per employee for SaaS

                data["team_metrics"] = {
                    "current_size": team_size,
                    "revenue_per_employee": round(revenue_per_employee, 2),
                    "expense_per_employee": round(expense_per_employee, 2),
                    "target_revenue_per_employee": target_revenue_per_employee,
                }

                # Hiring recommendations
                if monthly_revenue > 0 and revenue_per_employee > 0:
                    optimal_team_size = math.ceil(monthly_revenue / target_revenue_per_employee)
                    data["team_metrics"]["recommended_team_size"] = optimal_team_size
                    data["team_metrics"]["hiring_gap"] = optimal_team_size - team_size

            # Pricing analysis
            if cac > 0 and ltv > 0:
                ltv_cac_ratio = ltv / cac
                payback_months = self._estimate_payback_period(cac, monthly_revenue, gross_margin)

                data["pricing_metrics"] = {
                    "ltv": ltv,
                    "cac": cac,
                    "ltv_cac_ratio": round(ltv_cac_ratio, 2),
                    "target_ltv_cac_ratio": 3.0,
                    "payback_period_months": round(payback_months, 1),
                    "target_payback_months": 12,
                }

                # Pricing recommendations
                if ltv_cac_ratio < 3:
                    data["pricing_recommendations"] = {
                        "action": "Consider raising prices or reducing CAC",
                        "target_ltv": round(cac * 3, 2),
                        "price_increase_needed_percent": round(
                            ((cac * 3 / ltv) - 1) * 100, 1
                        ) if ltv > 0 else 0,
                    }

            # Cost structure analysis
            if monthly_revenue > 0:
                expense_ratio = monthly_expenses / monthly_revenue

                data["cost_structure"] = {
                    "total_expenses": monthly_expenses,
                    "revenue": monthly_revenue,
                    "expense_ratio": round(expense_ratio, 2),
                    "gross_margin": round(gross_margin, 2),
                }

                # Salary budget (typically 40-60% of expenses for startups)
                estimated_salary_budget = monthly_expenses * 0.5
                data["salary_budget"] = {
                    "estimated_monthly": round(estimated_salary_budget, 2),
                    "estimated_annual": round(estimated_salary_budget * 12, 2),
                    "percent_of_expenses": 50,
                }

        return data

    def _estimate_payback_period(
        self,
        cac: float,
        monthly_revenue: float,
        gross_margin: float,
    ) -> float:
        """
        Estimate CAC payback period in months.

        Formula: CAC / (ARPU * Gross Margin)
        """
        if monthly_revenue <= 0 or gross_margin <= 0:
            return 0

        # Rough ARPU estimate (assuming some customer base)
        # In reality, you'd get this from actual data
        arpu = monthly_revenue * 0.1  # Assume 10 customers contributing to MRR
        if arpu <= 0:
            return 0

        payback_months = cac / (arpu * gross_margin)
        return payback_months

    def _identify_warnings(
        self,
        task: AgentTask,
        data: Dict[str, Any],
    ) -> List[str]:
        """Identify operational warnings."""
        warnings = []

        # Team efficiency warnings
        if "team_metrics" in data:
            revenue_per_emp = data["team_metrics"].get("revenue_per_employee", 0)
            target = data["team_metrics"].get("target_revenue_per_employee", 15000)

            if revenue_per_emp > 0 and revenue_per_emp < target * 0.5:
                warnings.append(
                    f"Low revenue per employee: ${revenue_per_emp:,.0f} vs target ${target:,.0f}. "
                    "Consider optimizing team productivity or increasing revenue."
                )

        # Pricing warnings
        if "pricing_metrics" in data:
            ltv_cac = data["pricing_metrics"].get("ltv_cac_ratio", 0)
            if ltv_cac > 0 and ltv_cac < 3:
                warnings.append(
                    f"LTV:CAC ratio is {ltv_cac:.2f}, below the 3:1 target. "
                    "Consider raising prices or reducing customer acquisition costs."
                )

            payback = data["pricing_metrics"].get("payback_period_months", 0)
            if payback > 18:
                warnings.append(
                    f"CAC payback period is {payback:.1f} months, above 12-month target. "
                    "Unit economics need improvement."
                )

        # Cost structure warnings
        if "cost_structure" in data:
            expense_ratio = data["cost_structure"].get("expense_ratio", 0)
            if expense_ratio > 1.5:
                warnings.append(
                    f"Spending {expense_ratio:.1f}x revenue. "
                    "High burn rate - consider cost reduction initiatives."
                )

        return warnings
