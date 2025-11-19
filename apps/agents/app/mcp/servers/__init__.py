"""MCP servers for different tool categories."""

from .finance_server import create_finance_server
from .tax_server import create_tax_server
from .market_server import create_market_server
from .legal_server import create_legal_server
from .wealth_server import create_wealth_server
from .data_server import create_data_server
from .investor_server import create_investor_server
from .operations_server import create_operations_server

__all__ = [
    "create_finance_server",
    "create_tax_server",
    "create_market_server",
    "create_legal_server",
    "create_wealth_server",
    "create_data_server",
    "create_investor_server",
    "create_operations_server",
]


def initialize_all_servers():
    """Initialize and register all MCP servers."""
    from ..registry import MCPRegistry

    servers = [
        create_finance_server(),
        create_tax_server(),
        create_market_server(),
        create_legal_server(),
        create_wealth_server(),
        create_data_server(),
        create_investor_server(),
        create_operations_server(),
    ]

    for server in servers:
        MCPRegistry.register_server(server)

    return servers
