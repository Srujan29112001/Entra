"""MCP server for market and strategy tools."""

from ..protocol import MCPServer, MCPTool, MCPToolParameter
from app.tools.strategy_frameworks import (
    generate_swot_analysis,
    analyze_market_size,
    recommend_pricing_strategy,
    generate_gtm_plan,
)


def create_market_server() -> MCPServer:
    """Create and configure the Market & Strategy MCP server."""
    server = MCPServer(
        name="market",
        description="Market analysis, strategy frameworks, and GTM planning",
    )

    # SWOT analysis
    server.register_tool(
        MCPTool(
            name="generate_swot_analysis",
            description="Generate SWOT analysis for a business",
            parameters=[
                MCPToolParameter(
                    name="business_description",
                    type="string",
                    description="Description of the business",
                    required=True,
                ),
                MCPToolParameter(
                    name="industry",
                    type="string",
                    description="Industry sector",
                    required=True,
                ),
                MCPToolParameter(
                    name="target_market",
                    type="string",
                    description="Target market description",
                    required=True,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "strengths": {"type": "array"},
                    "weaknesses": {"type": "array"},
                    "opportunities": {"type": "array"},
                    "threats": {"type": "array"},
                },
            },
            category="market",
        ),
        generate_swot_analysis,
    )

    # Market size analysis
    server.register_tool(
        MCPTool(
            name="analyze_market_size",
            description="Analyze TAM, SAM, SOM for a market",
            parameters=[
                MCPToolParameter(
                    name="industry",
                    type="string",
                    description="Industry sector",
                    required=True,
                ),
                MCPToolParameter(
                    name="geography",
                    type="string",
                    description="Geographic market",
                    required=True,
                ),
                MCPToolParameter(
                    name="segment",
                    type="string",
                    description="Market segment",
                    required=False,
                    default="general",
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "tam": {"type": "number"},
                    "sam": {"type": "number"},
                    "som": {"type": "number"},
                },
            },
            category="market",
        ),
        analyze_market_size,
    )

    # Pricing strategy
    server.register_tool(
        MCPTool(
            name="recommend_pricing_strategy",
            description="Recommend optimal pricing strategy",
            parameters=[
                MCPToolParameter(
                    name="product_type",
                    type="string",
                    description="Type of product/service",
                    required=True,
                ),
                MCPToolParameter(
                    name="target_customer",
                    type="string",
                    description="Target customer segment",
                    required=True,
                ),
                MCPToolParameter(
                    name="cost_structure",
                    type="object",
                    description="Cost breakdown",
                    required=True,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "recommended_price": {"type": "number"},
                    "strategy": {"type": "string"},
                    "reasoning": {"type": "string"},
                },
            },
            category="market",
        ),
        recommend_pricing_strategy,
    )

    # GTM plan
    server.register_tool(
        MCPTool(
            name="generate_gtm_plan",
            description="Generate go-to-market plan",
            parameters=[
                MCPToolParameter(
                    name="product_description",
                    type="string",
                    description="Product description",
                    required=True,
                ),
                MCPToolParameter(
                    name="target_market",
                    type="string",
                    description="Target market",
                    required=True,
                ),
                MCPToolParameter(
                    name="budget",
                    type="number",
                    description="Available budget",
                    required=True,
                ),
                MCPToolParameter(
                    name="timeline_months",
                    type="number",
                    description="Timeline in months",
                    required=False,
                    default=6,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "channels": {"type": "array"},
                    "phases": {"type": "array"},
                    "budget_allocation": {"type": "object"},
                },
            },
            category="market",
        ),
        generate_gtm_plan,
    )

    return server
