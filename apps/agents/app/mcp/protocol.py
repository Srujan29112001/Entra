"""
Model Context Protocol (MCP) implementation.

This module implements the MCP standard for agent-tool communication,
enabling standardized, discoverable, and composable tool interfaces.

Based on: https://modelcontextprotocol.io/
"""

from typing import Any, Callable, Optional, Dict, List
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import uuid
from datetime import datetime
import json


class MCPMessageType(str, Enum):
    """MCP message types."""

    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    NOTIFICATION = "notification"


class MCPToolParameter(BaseModel):
    """MCP tool parameter definition."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None


class MCPTool(BaseModel):
    """
    MCP tool definition.

    Represents a callable tool that can be invoked by agents through
    the Model Context Protocol.
    """

    name: str
    description: str
    parameters: List[MCPToolParameter]
    returns: Dict[str, Any]
    category: str  # finance, tax, market, legal, wealth, data
    version: str = "1.0.0"
    handler: Optional[Callable] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert MCP tool to OpenAI function calling format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def to_anthropic_tool(self) -> Dict[str, Any]:
        """Convert MCP tool to Anthropic tool use format."""
        input_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for param in self.parameters:
            input_schema["properties"][param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                input_schema["properties"][param.name]["enum"] = param.enum
            if param.required:
                input_schema["required"].append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": input_schema,
        }


class MCPMessage(BaseModel):
    """MCP protocol message."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MCPMessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MCPServer:
    """
    MCP Server implementation.

    Hosts MCP tools and handles requests from agents.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize MCP server.

        Args:
            name: Server name
            description: Server description
        """
        self.name = name
        self.description = description
        self.tools: Dict[str, MCPTool] = {}
        self._running = False

    def register_tool(self, tool: MCPTool, handler: Callable):
        """
        Register a tool with the server.

        Args:
            tool: MCP tool definition
            handler: Async function to handle tool calls
        """
        tool.handler = handler
        self.tools[tool.name] = tool

    def list_tools(self) -> List[MCPTool]:
        """List all registered tools."""
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(name)

    async def invoke_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MCPMessage:
        """
        Invoke a tool via MCP.

        Args:
            tool_name: Name of the tool to invoke
            parameters: Tool parameters
            metadata: Optional metadata for the call

        Returns:
            MCPMessage with result or error
        """
        request_msg = MCPMessage(
            type=MCPMessageType.REQUEST,
            tool_name=tool_name,
            parameters=parameters,
            metadata=metadata or {},
        )

        tool = self.tools.get(tool_name)
        if not tool:
            return MCPMessage(
                id=request_msg.id,
                type=MCPMessageType.ERROR,
                error=f"Tool '{tool_name}' not found",
            )

        if not tool.handler:
            return MCPMessage(
                id=request_msg.id,
                type=MCPMessageType.ERROR,
                error=f"No handler registered for tool '{tool_name}'",
            )

        try:
            # Validate parameters
            self._validate_parameters(tool, parameters)

            # Invoke handler
            result = await tool.handler(**parameters)

            return MCPMessage(
                id=request_msg.id,
                type=MCPMessageType.RESPONSE,
                tool_name=tool_name,
                result=result,
                metadata={"execution_time_ms": (datetime.utcnow() - request_msg.timestamp).total_seconds() * 1000},
            )

        except Exception as e:
            return MCPMessage(
                id=request_msg.id,
                type=MCPMessageType.ERROR,
                tool_name=tool_name,
                error=str(e),
            )

    def _validate_parameters(self, tool: MCPTool, parameters: Dict[str, Any]):
        """Validate tool parameters."""
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                raise ValueError(f"Missing required parameter: {param.name}")

            if param.name in parameters and param.enum:
                if parameters[param.name] not in param.enum:
                    raise ValueError(
                        f"Invalid value for {param.name}. "
                        f"Must be one of: {param.enum}"
                    )

    async def start(self):
        """Start the MCP server."""
        self._running = True
        print(f"MCP Server '{self.name}' started with {len(self.tools)} tools")

    async def stop(self):
        """Stop the MCP server."""
        self._running = False
        print(f"MCP Server '{self.name}' stopped")


class MCPClient:
    """
    MCP Client implementation.

    Connects to MCP servers and invokes tools.
    """

    def __init__(self, agent_id: str):
        """
        Initialize MCP client.

        Args:
            agent_id: Identifier for the agent using this client
        """
        self.agent_id = agent_id
        self.servers: Dict[str, MCPServer] = {}

    def register_server(self, server: MCPServer):
        """Register an MCP server."""
        self.servers[server.name] = server

    def discover_tools(self, category: Optional[str] = None) -> List[MCPTool]:
        """
        Discover available tools across all servers.

        Args:
            category: Optional category filter

        Returns:
            List of available tools
        """
        tools = []
        for server in self.servers.values():
            server_tools = server.list_tools()
            if category:
                server_tools = [t for t in server_tools if t.category == category]
            tools.extend(server_tools)
        return tools

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        server_name: Optional[str] = None,
    ) -> MCPMessage:
        """
        Call a tool via MCP.

        Args:
            tool_name: Name of the tool to call
            parameters: Tool parameters
            server_name: Optional server name (auto-discovered if not provided)

        Returns:
            MCPMessage with result or error
        """
        # Find the server hosting this tool
        if server_name:
            server = self.servers.get(server_name)
            if not server:
                return MCPMessage(
                    type=MCPMessageType.ERROR,
                    error=f"Server '{server_name}' not found",
                )
        else:
            server = None
            for s in self.servers.values():
                if s.get_tool(tool_name):
                    server = s
                    break

            if not server:
                return MCPMessage(
                    type=MCPMessageType.ERROR,
                    error=f"No server found hosting tool '{tool_name}'",
                )

        # Invoke the tool
        return await server.invoke_tool(
            tool_name,
            parameters,
            metadata={"agent_id": self.agent_id},
        )

    def get_tools_for_llm(
        self,
        format: str = "openai",
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get tool definitions formatted for LLM function calling.

        Args:
            format: Either "openai" or "anthropic"
            category: Optional category filter

        Returns:
            List of tool definitions in the requested format
        """
        tools = self.discover_tools(category)

        if format == "openai":
            return [tool.to_openai_function() for tool in tools]
        elif format == "anthropic":
            return [tool.to_anthropic_tool() for tool in tools]
        else:
            raise ValueError(f"Unsupported format: {format}")
