"""
Agent-to-Agent (A2A) Communication Protocol.

Enables agents to communicate, delegate tasks, and collaborate
on complex multi-domain problems.
"""

from .protocol import A2AMessage, A2AMessageType, A2AProtocol
from .router import A2ARouter

__all__ = ["A2AMessage", "A2AMessageType", "A2AProtocol", "A2ARouter"]
