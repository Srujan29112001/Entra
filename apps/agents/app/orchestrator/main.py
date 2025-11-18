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
        - finance: Financial planning, runway, funding strategy
        - tax: Tax optimization, policy compliance
        - market: Market strategy, distribution, GTM
        - legal: Contract analysis, compliance
        - wealth: Personal wealth, salary optimization

        Question: {state['question']}
        Context: {state.get('context', {{}})}

        Respond with:
        1. Task type (finance/tax/market/legal/wealth/composite)
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

            # Execute agent
            if agent_type == "finance":
                agent = FinanceAgent()
                response = await agent.process(task)
                responses.append(response)
            elif agent_type == "tax":
                agent = TaxPolicyAgent()
                response = await agent.process(task)
                responses.append(response)
            elif agent_type == "market":
                agent = MarketStrategyAgent()
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

        return OrchestratorResponse(
            task_id=task_id,
            final_answer=final_state["final_answer"],
            agent_responses=final_state["agent_responses"],
            chart_data=None,  # TODO: Extract chart data from responses
            metadata=final_state["metadata"],
        )
