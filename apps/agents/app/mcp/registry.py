"""MCP Registry for managing servers and tools."""

from typing import Dict, List, Optional
from .protocol import MCPServer, MCPTool, MCPClient


class MCPRegistry:
    """
    Global registry for MCP servers and tools.

    Provides centralized management and discovery of all MCP servers
    and tools in the system.
    """

    _instance: Optional["MCPRegistry"] = None
    _servers: Dict[str, MCPServer] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_server(cls, server: MCPServer):
        """Register an MCP server."""
        cls._servers[server.name] = server
        print(f"Registered MCP server: {server.name} ({len(server.tools)} tools)")

    @classmethod
    def get_server(cls, name: str) -> Optional[MCPServer]:
        """Get a server by name."""
        return cls._servers.get(name)

    @classmethod
    def list_servers(cls) -> List[MCPServer]:
        """List all registered servers."""
        return list(cls._servers.values())

    @classmethod
    def discover_all_tools(cls) -> List[MCPTool]:
        """Discover all tools across all servers."""
        tools = []
        for server in cls._servers.values():
            tools.extend(server.list_tools())
        return tools

    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[MCPTool]:
        """Find a tool by name across all servers."""
        for server in cls._servers.values():
            tool = server.get_tool(tool_name)
            if tool:
                return tool
        return None

    @classmethod
    def create_client(cls, agent_id: str) -> MCPClient:
        """
        Create an MCP client with all registered servers.

        Args:
            agent_id: Identifier for the agent

        Returns:
            MCPClient configured with all servers
        """
        client = MCPClient(agent_id)
        for server in cls._servers.values():
            client.register_server(server)
        return client

    @classmethod
    async def start_all_servers(cls):
        """Start all registered servers."""
        for server in cls._servers.values():
            await server.start()

    @classmethod
    async def stop_all_servers(cls):
        """Stop all registered servers."""
        for server in cls._servers.values():
            await server.stop()
