"""
A2A (Agent-to-Agent) Protocol Implementation.

Enables structured communication and task delegation between AI agents.
Based on emerging A2A standards for multi-agent systems.
"""

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import uuid


class A2AMessageType(str, Enum):
    """Types of A2A messages."""

    REQUEST = "request"  # Agent requests another agent's help
    RESPONSE = "response"  # Agent responds to a request
    DELEGATE = "delegate"  # Agent delegates a task
    QUERY = "query"  # Agent queries another agent's state/capability
    NOTIFY = "notify"  # Agent notifies others of an event
    ERROR = "error"  # Error in processing


class A2AMessage(BaseModel):
    """
    Standard A2A message format.

    Enables agents to communicate with structured, typed messages.
    """

    # Message identification
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )  # Groups related messages
    parent_id: Optional[str] = None  # For threading/replies

    # Message routing
    from_agent: str  # Sender agent type (e.g., "finance", "tax")
    to_agent: str  # Recipient agent type
    message_type: A2AMessageType

    # Message content
    subject: str  # Brief description of the request/topic
    content: Dict[str, Any]  # Structured content
    priority: int = Field(default=1, ge=1, le=5)  # 1=highest, 5=lowest

    # Context
    context: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = True

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: Optional[int] = 300  # Time to live (5 min default)

    # Tracing
    trace_id: Optional[str] = None  # For distributed tracing
    user_id: Optional[str] = None
    company_id: Optional[str] = None


class A2AProtocol:
    """
    A2A Protocol handler.

    Manages message routing, validation, and delivery between agents.
    """

    def __init__(self):
        """Initialize A2A protocol."""
        self.message_queue: Dict[str, List[A2AMessage]] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.message_history: List[A2AMessage] = []

    def register_agent(self, agent_type: str, capabilities: List[str]):
        """
        Register an agent and its capabilities.

        Args:
            agent_type: Type of agent (finance, tax, etc.)
            capabilities: List of capabilities this agent provides
        """
        self.agent_capabilities[agent_type] = capabilities
        self.message_queue[agent_type] = []
        print(f"A2A: Registered agent '{agent_type}' with {len(capabilities)} capabilities")

    async def send_message(self, message: A2AMessage) -> bool:
        """
        Send a message from one agent to another.

        Args:
            message: A2A message to send

        Returns:
            True if successfully queued
        """
        # Validate recipient exists
        if message.to_agent not in self.message_queue:
            raise ValueError(f"Agent '{message.to_agent}' not registered")

        # Queue message for recipient
        self.message_queue[message.to_agent].append(message)
        self.message_history.append(message)

        print(
            f"A2A: {message.from_agent} → {message.to_agent} | "
            f"{message.message_type.value} | {message.subject}"
        )

        return True

    async def receive_messages(
        self, agent_type: str, limit: int = 10
    ) -> List[A2AMessage]:
        """
        Receive pending messages for an agent.

        Args:
            agent_type: Type of agent receiving messages
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages for this agent
        """
        if agent_type not in self.message_queue:
            return []

        messages = self.message_queue[agent_type][:limit]
        self.message_queue[agent_type] = self.message_queue[agent_type][limit:]
        return messages

    async def request_help(
        self,
        from_agent: str,
        to_agent: str,
        task_description: str,
        context: Dict[str, Any],
        conversation_id: Optional[str] = None,
    ) -> A2AMessage:
        """
        Helper: One agent requests help from another.

        Args:
            from_agent: Requesting agent
            to_agent: Agent to help
            task_description: What help is needed
            context: Relevant context data
            conversation_id: Optional conversation ID to group messages

        Returns:
            The sent message
        """
        message = A2AMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=A2AMessageType.REQUEST,
            subject=task_description,
            content={"task": task_description, "context": context},
            context=context,
            conversation_id=conversation_id or str(uuid.uuid4()),
        )

        await self.send_message(message)
        return message

    async def delegate_task(
        self,
        from_agent: str,
        to_agent: str,
        task: Dict[str, Any],
        context: Dict[str, Any],
    ) -> A2AMessage:
        """
        Helper: Delegate a task to another agent.

        Args:
            from_agent: Delegating agent
            to_agent: Agent to execute task
            task: Task definition
            context: Context data

        Returns:
            The sent message
        """
        message = A2AMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=A2AMessageType.DELEGATE,
            subject=f"Delegated: {task.get('type', 'task')}",
            content=task,
            context=context,
        )

        await self.send_message(message)
        return message

    def get_conversation(self, conversation_id: str) -> List[A2AMessage]:
        """Get all messages in a conversation."""
        return [
            msg for msg in self.message_history if msg.conversation_id == conversation_id
        ]

    def get_capable_agents(self, capability: str) -> List[str]:
        """Find agents that have a specific capability."""
        return [
            agent
            for agent, caps in self.agent_capabilities.items()
            if capability in caps
        ]


# Global A2A protocol instance (singleton)
_a2a_protocol: Optional[A2AProtocol] = None


def get_a2a_protocol() -> A2AProtocol:
    """Get the global A2A protocol instance."""
    global _a2a_protocol
    if _a2a_protocol is None:
        _a2a_protocol = A2AProtocol()
    return _a2a_protocol
