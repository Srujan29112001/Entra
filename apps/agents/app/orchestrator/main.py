"""Multi-Agent Orchestrator using LangGraph."""

from typing import Any, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
import uuid
from app.config import settings
from app.models.schemas import (
    AgentTask,
    AgentResponse,
    OrchestratorResponse,
    TaskType,
)


class OrchestratorState(TypedDict):
    """State for the orchestrator graph."""

    messages: list[BaseMessage]
    user_id: str
    company_id: str
    question: str
    context: dict[str, Any]
    task_type: TaskType | None
    agent_responses: list[AgentResponse]
    final_answer: str | None
    metadata: dict[str, Any]


class OrchestratorService:
    """
    Multi-agent orchestrator service.

    This service coordinates multiple specialist agents to handle
    complex queries that span multiple domains (finance, tax, strategy, etc.).

    Architecture:
    1. Planner: Analyzes the question and decides which agents to involve
    2. Agent Execution: Runs specialist agents in parallel or sequence
    3. Aggregator: Combines agent outputs into a coherent response
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self.llm = ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0.7,
        )
        self.planner_llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.3,
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph orchestration graph."""
        workflow = StateGraph(OrchestratorState)

        # Define nodes
        workflow.add_node("planner", self._plan_task)
        workflow.add_node("execute_agents", self._execute_agents)
        workflow.add_node("aggregator", self._aggregate_responses)

        # Define edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "execute_agents")
        workflow.add_edge("execute_agents", "aggregator")
        workflow.add_edge("aggregator", END)

        return workflow.compile()

    async def _plan_task(self, state: OrchestratorState) -> OrchestratorState:
        """
        Plan which agents to invoke based on the question.

        Uses an LLM to classify the task and determine which specialist
        agents are needed.
        """
        planning_prompt = f"""
        Analyze this question and determine which specialist agents should handle it.

        Available agents:
        - finance: Financial planning, runway, cash flow, funding strategy
        - tax: Tax optimization, policy compliance, salary vs dividend
        - market: Market strategy, distribution, GTM, competitive analysis
        - legal: Contract analysis, compliance, risk assessment
        - wealth: Personal wealth, salary optimization, ESOP, portfolio
        - investor: Fundraising, pitch preparation, investor relations, valuation
        - operations: Pricing, team planning, hiring, resource allocation

        Question: {state['question']}
        Context: {state.get('context', {{}})}

        Respond with:
        1. Task type (finance/tax/market/legal/wealth/investor/operations/composite)
        2. List of agents needed
        3. Complexity (simple/medium/complex)

        Format as JSON.
        """

        messages = [HumanMessage(content=planning_prompt)]
        response = await self.planner_llm.ainvoke(messages)

        # Parse response (simplified - in production, use structured output)
        # For now, default to composite task using all agents
        state["task_type"] = TaskType(
            type="composite",
            agents_required=["finance", "tax", "market"],
            complexity="medium",
        )
        state["metadata"] = {"planning": "completed"}

        return state

    async def _execute_agents(self, state: OrchestratorState) -> OrchestratorState:
        """
        Execute the required specialist agents.

        Agents can run in parallel for independent tasks or sequentially
        if outputs depend on each other.
        """
        from app.agents.finance_agent import FinanceAgent
        from app.agents.tax_agent import TaxPolicyAgent
        from app.agents.market_agent import MarketStrategyAgent
        from app.agents.legal_agent import LegalComplianceAgent
        from app.agents.wealth_agent import PersonalWealthAgent
        from app.agents.investor_agent import InvestorRelationsAgent
        from app.agents.operations_agent import OperationsAgent

        task_id = str(uuid.uuid4())
        responses = []

        # Create tasks for each agent
        for agent_type in state["task_type"].agents_required:
            task = AgentTask(
                task_id=task_id,
                agent_type=agent_type,
                question=state["question"],
                context=state["context"],
                user_id=state["user_id"],
                company_id=state["company_id"],
            )

            # Execute agent based on type
            agent = None
            if agent_type == "finance":
                agent = FinanceAgent()
            elif agent_type == "tax":
                agent = TaxPolicyAgent()
            elif agent_type == "market":
                agent = MarketStrategyAgent()
            elif agent_type == "legal":
                agent = LegalComplianceAgent()
            elif agent_type == "wealth":
                agent = PersonalWealthAgent()
            elif agent_type == "investor":
                agent = InvestorRelationsAgent()
            elif agent_type == "operations":
                agent = OperationsAgent()

            if agent:
                response = await agent.process(task)
                responses.append(response)

        state["agent_responses"] = responses
        return state

    async def _aggregate_responses(self, state: OrchestratorState) -> OrchestratorState:
        """
        Aggregate all agent responses into a final coherent answer.

        Uses an LLM to synthesize the specialist outputs into a
        comprehensive response.
        """
        aggregation_prompt = f"""
        Synthesize these specialist agent responses into a comprehensive answer.

        Original question: {state['question']}

        Agent responses:
        {self._format_agent_responses(state['agent_responses'])}

        Provide a clear, actionable answer that:
        1. Addresses the user's question directly
        2. Integrates insights from all agents
        3. Highlights key numbers and recommendations
        4. Notes any conflicts or trade-offs
        """

        messages = [HumanMessage(content=aggregation_prompt)]
        response = await self.llm.ainvoke(messages)

        state["final_answer"] = response.content
        state["metadata"]["aggregation"] = "completed"

        return state

    def _format_agent_responses(self, responses: list[AgentResponse]) -> str:
        """Format agent responses for aggregation."""
        formatted = []
        for resp in responses:
            formatted.append(f"\n{resp.agent_type.upper()} AGENT:\n{resp.answer}")
            if resp.warnings:
                formatted.append(f"Warnings: {', '.join(resp.warnings)}")
        return "\n".join(formatted)

    async def process_request(
        self,
        user_id: str,
        company_id: str,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> OrchestratorResponse:
        """
        Process a user request through the multi-agent orchestrator.

        Args:
            user_id: User identifier
            company_id: Company identifier
            question: User's question
            context: Optional context data

        Returns:
            OrchestratorResponse with final answer and agent outputs
        """
        task_id = str(uuid.uuid4())

        initial_state: OrchestratorState = {
            "messages": [HumanMessage(content=question)],
            "user_id": user_id,
            "company_id": company_id,
            "question": question,
            "context": context or {},
            "task_type": None,
            "agent_responses": [],
            "final_answer": None,
            "metadata": {"task_id": task_id},
        }

        # Run through the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Extract chart data from agent responses
        chart_data = self._extract_chart_data(final_state["agent_responses"])

        return OrchestratorResponse(
            task_id=task_id,
            final_answer=final_state["final_answer"],
            agent_responses=final_state["agent_responses"],
            chart_data=chart_data,
            metadata=final_state["metadata"],
        )

    def _extract_chart_data(self, responses: list[AgentResponse]) -> dict[str, Any] | None:
        """
        Extract chart-worthy data from agent responses.

        Looks for numerical data, projections, comparisons that can be visualized.

        Args:
            responses: List of agent responses

        Returns:
            Dictionary of chart data or None
        """
        chart_data = {
            "financial_metrics": [],
            "projections": [],
            "comparisons": [],
            "time_series": [],
        }

        for response in responses:
            # Extract data from the response's data field
            if response.data:
                agent_data = response.data

                # Finance agent data
                if response.agent_type == "finance":
                    if "runway" in agent_data:
                        chart_data["financial_metrics"].append({
                            "name": "Runway (months)",
                            "value": agent_data["runway"],
                            "type": "metric"
                        })
                    if "burn_rate" in agent_data:
                        chart_data["financial_metrics"].append({
                            "name": "Monthly Burn Rate",
                            "value": agent_data["burn_rate"],
                            "type": "metric"
                        })
                    if "projections" in agent_data:
                        chart_data["projections"] = agent_data["projections"]

                # Tax agent data
                elif response.agent_type == "tax":
                    if "tax_breakdown" in agent_data:
                        chart_data["comparisons"].append({
                            "category": "Tax Structure",
                            "data": agent_data["tax_breakdown"],
                        })

                # Market agent data
                elif response.agent_type == "market":
                    if "market_size" in agent_data:
                        chart_data["comparisons"].append({
                            "category": "Market Size",
                            "data": agent_data["market_size"],
                        })
                    if "growth_projections" in agent_data:
                        chart_data["time_series"].append({
                            "series": "Market Growth",
                            "data": agent_data["growth_projections"],
                        })

        # Return None if no chart data was extracted
        if (not chart_data["financial_metrics"] and
            not chart_data["projections"] and
            not chart_data["comparisons"] and
            not chart_data["time_series"]):
            return None

        return chart_data
