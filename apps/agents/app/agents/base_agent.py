"""Base agent class for all specialist agents."""

from abc import ABC, abstractmethod
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings
from app.models.schemas import AgentTask, AgentResponse
from app.mcp.protocol import MCPClient
from app.mcp.registry import MCPRegistry
from typing import Any


class BaseAgent(ABC):
    """
    Base class for all specialist agents.

    Each specialist agent inherits from this and implements:
    - system_prompt: Defines the agent's role and capabilities
    - process: Main logic to handle tasks
    - _get_tools: Tools specific to this agent (via MCP)
    """

    def __init__(self, use_claude: bool = True):
        """Initialize the agent with an LLM and MCP client."""
        if use_claude:
            self.llm = ChatAnthropic(
                model=settings.anthropic_model,
                api_key=settings.anthropic_api_key,
                temperature=0.7,
            )
        else:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0.7,
            )

        # Initialize MCP client for standardized tool access
        self.mcp_client = MCPRegistry.create_client(self.agent_type)

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return the agent type identifier."""
        pass

    @abstractmethod
    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process a task and return a response.

        This is the main method that handles the agent's logic.
        """
        pass

    async def _call_llm(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """
        Call the LLM with the agent's system prompt and user prompt.

        Args:
            prompt: The user's question or task
            context: Optional context data

        Returns:
            The LLM's response as a string
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=self._format_prompt(prompt, context)),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content

    def _format_prompt(self, prompt: str, context: dict[str, Any] | None) -> str:
        """Format the prompt with context."""
        if not context:
            return prompt

        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        return f"Context:\n{context_str}\n\nQuestion:\n{prompt}"

    async def _retrieve_context(
        self, query: str, company_id: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant context from RAG system.

        Args:
            query: Search query
            company_id: Company identifier for filtering
            top_k: Number of results to return

        Returns:
            List of relevant documents/chunks
        """
        from app.rag.retriever import RAGRetriever

        retriever = RAGRetriever()
        results = await retriever.retrieve(query, company_id=company_id, top_k=top_k)
        return results

    async def _call_mcp_tool(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> Any:
        """
        Call a tool via MCP (Model Context Protocol).

        This provides standardized, protocol-based tool access across all agents.

        Args:
            tool_name: Name of the MCP tool to call
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        response = await self.mcp_client.call_tool(tool_name, parameters)

        if response.type.value == "error":
            raise RuntimeError(f"MCP tool error: {response.error}")

        return response.result

    def _get_mcp_tools_for_llm(self, category: str = None) -> list[dict[str, Any]]:
        """
        Get MCP tools formatted for LLM function calling.

        Args:
            category: Optional category filter (e.g., "finance", "tax")

        Returns:
            List of tool definitions for LLM
        """
        # Detect LLM type and format accordingly
        if isinstance(self.llm, ChatAnthropic):
            return self.mcp_client.get_tools_for_llm(format="anthropic", category=category)
        else:
            return self.mcp_client.get_tools_for_llm(format="openai", category=category)
