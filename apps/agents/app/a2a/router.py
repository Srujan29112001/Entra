"""
A2A Router for intelligent message routing and orchestration.

Routes messages between agents based on capabilities, load, and priority.
"""

from typing import List, Dict, Any, Optional
from .protocol import A2AMessage, A2AProtocol, get_a2a_protocol
import asyncio


class A2ARouter:
    """
    Intelligent router for A2A messages.

    Routes messages to the most appropriate agent based on:
    - Agent capabilities
    - Current load
    - Message priority
    - Historical performance
    """

    def __init__(self, protocol: Optional[A2AProtocol] = None):
        """Initialize router."""
        self.protocol = protocol or get_a2a_protocol()
        self.agent_load: Dict[str, int] = {}  # Track pending messages per agent

    async def route_query(
        self,
        from_agent: str,
        query: str,
        context: Dict[str, Any],
        required_capabilities: List[str],
    ) -> List[A2AMessage]:
        """
        Route a query to all agents with required capabilities.

        Args:
            from_agent: Querying agent
            query: The query
            context: Context data
            required_capabilities: List of required capabilities

        Returns:
            List of sent messages
        """
        messages = []

        for capability in required_capabilities:
            capable_agents = self.protocol.get_capable_agents(capability)

            for agent in capable_agents:
                if agent == from_agent:
                    continue  # Don't message yourself

                message = await self.protocol.request_help(
                    from_agent=from_agent,
                    to_agent=agent,
                    task_description=query,
                    context=context,
                )
                messages.append(message)

        return messages

    async def route_to_best_agent(
        self,
        from_agent: str,
        task: Dict[str, Any],
        capability: str,
        context: Dict[str, Any],
    ) -> Optional[A2AMessage]:
        """
        Route a task to the best agent for a capability.

        "Best" is determined by current load (fewer pending messages).

        Args:
            from_agent: Requesting agent
            task: Task to delegate
            capability: Required capability
            context: Context data

        Returns:
            Sent message or None if no capable agent found
        """
        capable_agents = self.protocol.get_capable_agents(capability)
        capable_agents = [a for a in capable_agents if a != from_agent]

        if not capable_agents:
            return None

        # Find agent with lowest load
        best_agent = min(capable_agents, key=lambda a: self.agent_load.get(a, 0))

        message = await self.protocol.delegate_task(
            from_agent=from_agent,
            to_agent=best_agent,
            task=task,
            context=context,
        )

        # Update load tracking
        self.agent_load[best_agent] = self.agent_load.get(best_agent, 0) + 1

        return message

    async def broadcast(
        self,
        from_agent: str,
        notification: str,
        data: Dict[str, Any],
        exclude_agents: Optional[List[str]] = None,
    ) -> List[A2AMessage]:
        """
        Broadcast a notification to all agents.

        Args:
            from_agent: Sending agent
            notification: Notification subject
            data: Notification data
            exclude_agents: Agents to exclude from broadcast

        Returns:
            List of sent messages
        """
        from .protocol import A2AMessageType

        exclude_agents = exclude_agents or []
        exclude_agents.append(from_agent)  # Don't notify self

        messages = []
        for agent_type in self.protocol.agent_capabilities.keys():
            if agent_type in exclude_agents:
                continue

            message = A2AMessage(
                from_agent=from_agent,
                to_agent=agent_type,
                message_type=A2AMessageType.NOTIFY,
                subject=notification,
                content=data,
                requires_response=False,
            )

            await self.protocol.send_message(message)
            messages.append(message)

        return messages

    def update_agent_load(self, agent_type: str, delta: int):
        """
        Update the load counter for an agent.

        Args:
            agent_type: Agent type
            delta: Change in load (+1 for new task, -1 for completed task)
        """
        self.agent_load[agent_type] = max(0, self.agent_load.get(agent_type, 0) + delta)
