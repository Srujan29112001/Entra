"""
Investor Relations Agent.

Handles pitch simulation, funding strategy evaluation, venture capital analysis,
and investor communication.
"""

from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse
from app.mcp.registry import MCPRegistry
from app.rag.retriever import retriever
from langchain_core.messages import HumanMessage


class InvestorRelationsAgent(BaseAgent):
    """
    Investor Relations Agent.

    Specializes in:
    - Pitch deck analysis and improvement
    - Funding round strategy (seed, Series A/B/C)
    - Investor matching and outreach
    - Valuation modeling
    - Cap table management
    - Investor updates and reporting
    """

    def __init__(self):
        """Initialize Investor Relations Agent."""
        super().__init__(
            agent_type="investor",
            capabilities=[
                "pitch_deck_analysis",
                "funding_strategy",
                "investor_matching",
                "valuation_modeling",
                "cap_table_management",
                "investor_updates",
                "term_sheet_review",
                "due_diligence_prep",
            ],
        )

    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process an investor relations task.

        Args:
            task: Agent task containing the question and context

        Returns:
            AgentResponse with investor advice
        """
        # Get MCP client
        mcp_client = await MCPRegistry.get_client("investor_agent")

        # Retrieve relevant knowledge from RAG
        relevant_docs = await retriever.retrieve(
            query=task.question,
            company_id=task.company_id,
            document_type="pitch_deck",
            top_k=3,
        )

        # Build context for LLM
        context_parts = []

        # Add company context
        if task.context:
            company_info = f"""
            Company Stage: {task.context.get('stage', 'unknown')}
            Industry: {task.context.get('industry', 'unknown')}
            Country: {task.context.get('country', 'unknown')}
            Team Size: {task.context.get('team_size', 'unknown')}
            """
            context_parts.append(company_info)

        # Add financial context if available
        if task.context and 'financials' in task.context:
            fin = task.context['financials']
            financial_info = f"""
            Monthly Revenue: ${fin.get('monthly_revenue', 0):,.2f}
            Monthly Expenses: ${fin.get('monthly_expenses', 0):,.2f}
            Burn Rate: ${fin.get('burn_rate', 0):,.2f}
            Runway: {fin.get('runway_months', 0):.1f} months
            Total Funding: ${fin.get('total_funding', 0):,.2f}
            Valuation: ${fin.get('valuation', 0):,.2f}
            """
            context_parts.append(financial_info)

        # Add RAG context
        if relevant_docs:
            rag_context = "\n\n".join([doc['content'] for doc in relevant_docs])
            context_parts.append(f"Relevant Context:\n{rag_context}")

        full_context = "\n\n".join(context_parts)

        # Prepare prompt for LLM
        prompt = f"""
        You are an expert Investor Relations advisor specializing in startup fundraising,
        pitch preparation, and investor communication.

        Context:
        {full_context}

        Question: {task.question}

        Provide expert advice covering:
        1. Strategic recommendations
        2. Specific next steps
        3. Key metrics to highlight
        4. Potential red flags to address
        5. Investor communication tips

        Format your response as actionable advice with specific numbers and examples.
        """

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        answer = response.content

        # Extract structured data if possible
        data = await self._extract_investor_data(task, answer)

        # Identify warnings
        warnings = self._identify_warnings(task, data)

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=answer,
            data=data,
            warnings=warnings,
            confidence=0.85,
        )

    async def _extract_investor_data(
        self,
        task: AgentTask,
        answer: str,
    ) -> Dict[str, Any]:
        """Extract structured investor data from the response."""
        data = {}

        # Get financials from context
        if task.context and 'financials' in task.context:
            fin = task.context['financials']

            # Calculate key investor metrics
            monthly_revenue = fin.get('monthly_revenue', 0)
            monthly_expenses = fin.get('monthly_expenses', 0)
            burn_rate = abs(fin.get('burn_rate', monthly_expenses - monthly_revenue))
            runway_months = fin.get('runway_months', 0)
            total_funding = fin.get('total_funding', 0)
            valuation = fin.get('valuation', 0)

            # Determine funding stage recommendation
            stage = task.context.get('stage', 'unknown')
            funding_stage = self._recommend_funding_stage(
                stage, monthly_revenue, total_funding
            )

            # Calculate funding needs
            monthly_burn = burn_rate if burn_rate > 0 else monthly_expenses
            months_needed = 18  # Standard 18-month runway target
            funding_needed = monthly_burn * months_needed

            # Add buffer for growth
            growth_buffer = funding_needed * 0.3  # 30% buffer
            total_raise = funding_needed + growth_buffer

            data = {
                "funding_stage": funding_stage,
                "monthly_burn": round(monthly_burn, 2),
                "current_runway_months": round(runway_months, 1),
                "target_runway_months": months_needed,
                "recommended_raise": round(total_raise, 2),
                "base_funding_need": round(funding_needed, 2),
                "growth_buffer": round(growth_buffer, 2),
                "current_valuation": valuation,
                "key_metrics": {
                    "mrr": monthly_revenue,
                    "burn_rate": monthly_burn,
                    "runway": runway_months,
                },
            }

            # Add investor types based on stage
            data["target_investor_types"] = self._get_investor_types(funding_stage)

            # Add milestones to achieve before fundraising
            data["milestones_needed"] = self._get_milestones(
                funding_stage, monthly_revenue
            )

        return data

    def _recommend_funding_stage(
        self,
        company_stage: str,
        monthly_revenue: float,
        total_funding: float,
    ) -> str:
        """Recommend which funding round to pursue."""
        if company_stage in ['idea', 'mvp'] and total_funding == 0:
            return "Pre-Seed"
        elif company_stage in ['idea', 'mvp'] and total_funding < 500000:
            return "Seed"
        elif company_stage == 'seed' or (monthly_revenue > 0 and monthly_revenue < 100000):
            return "Seed"
        elif monthly_revenue >= 100000 and monthly_revenue < 500000:
            return "Series A"
        elif monthly_revenue >= 500000:
            return "Series B"
        else:
            return "Seed"

    def _get_investor_types(self, funding_stage: str) -> List[str]:
        """Get recommended investor types for a funding stage."""
        investor_map = {
            "Pre-Seed": [
                "Angel Investors",
                "Friends & Family",
                "Micro VCs",
                "Incubators/Accelerators",
            ],
            "Seed": [
                "Seed VCs",
                "Angel Groups",
                "Corporate VCs",
                "Strategic Investors",
            ],
            "Series A": [
                "Early-stage VCs",
                "Growth Funds",
                "Strategic Investors",
                "Family Offices",
            ],
            "Series B": [
                "Growth-stage VCs",
                "Corporate VCs",
                "Private Equity",
                "Hedge Funds",
            ],
        }
        return investor_map.get(funding_stage, ["Seed VCs", "Angel Investors"])

    def _get_milestones(
        self,
        funding_stage: str,
        monthly_revenue: float,
    ) -> List[str]:
        """Get key milestones needed before fundraising."""
        milestones_map = {
            "Pre-Seed": [
                "Working MVP or prototype",
                "Initial customer validation (10-50 users)",
                "Clear problem-solution fit",
                "Founding team assembled",
            ],
            "Seed": [
                "Product-market fit indicators",
                "Revenue traction ($10K-$50K MRR)",
                "Growing user base (1,000+ users)",
                "Clear unit economics path",
            ],
            "Series A": [
                "Proven business model",
                "$100K+ MRR with growth",
                "Strong customer retention",
                "Clear path to $1M ARR",
            ],
            "Series B": [
                "$500K+ MRR",
                "Proven scalability",
                "Established market position",
                "Clear expansion strategy",
            ],
        }
        return milestones_map.get(funding_stage, [])

    def _identify_warnings(
        self,
        task: AgentTask,
        data: Dict[str, Any],
    ) -> List[str]:
        """Identify investor relation warnings."""
        warnings = []

        if data:
            # Runway warning
            current_runway = data.get('current_runway_months', 0)
            if current_runway < 6:
                warnings.append(
                    f"Critical: Only {current_runway:.1f} months runway. "
                    "Start fundraising immediately."
                )
            elif current_runway < 9:
                warnings.append(
                    f"Start fundraising soon. {current_runway:.1f} months runway "
                    "gives limited time for a 3-6 month raise process."
                )

            # Burn rate warning
            monthly_burn = data.get('monthly_burn', 0)
            if task.context and 'financials' in task.context:
                monthly_revenue = task.context['financials'].get('monthly_revenue', 0)
                if monthly_revenue > 0:
                    burn_multiple = monthly_burn / monthly_revenue
                    if burn_multiple > 2:
                        warnings.append(
                            f"High burn rate: Spending {burn_multiple:.1f}x revenue. "
                            "Investors may question capital efficiency."
                        )

            # Valuation warning
            current_val = data.get('current_valuation', 0)
            if current_val == 0:
                warnings.append(
                    "No current valuation set. Consider getting a professional "
                    "409A valuation before fundraising."
                )

        return warnings
