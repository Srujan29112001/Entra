"""MCP server for financial tools."""

from typing import Dict, Any
from ..protocol import MCPServer, MCPTool, MCPToolParameter
from app.tools.financial_calculators import (
    calculate_runway,
    calculate_burn_rate,
    calculate_unit_economics,
    project_revenue,
    calculate_valuation,
)


def create_finance_server() -> MCPServer:
    """Create and configure the Finance MCP server."""
    server = MCPServer(
        name="finance",
        description="Financial planning, analysis, and projections",
    )

    # Register runway calculator
    runway_tool = MCPTool(
        name="calculate_runway",
        description="Calculate cash runway in months based on current cash and burn rate",
        parameters=[
            MCPToolParameter(
                name="current_cash",
                type="number",
                description="Current cash balance in dollars",
                required=True,
            ),
            MCPToolParameter(
                name="monthly_burn",
                type="number",
                description="Monthly burn rate in dollars",
                required=True,
            ),
            MCPToolParameter(
                name="expected_revenue",
                type="number",
                description="Expected monthly revenue in dollars",
                required=False,
                default=0,
            ),
        ],
        returns={"type": "object", "properties": {"runway_months": {"type": "number"}}},
        category="finance",
    )
    server.register_tool(runway_tool, calculate_runway)

    # Register burn rate calculator
    burn_rate_tool = MCPTool(
        name="calculate_burn_rate",
        description="Calculate monthly burn rate from expenses",
        parameters=[
            MCPToolParameter(
                name="monthly_expenses",
                type="object",
                description="Dictionary of monthly expenses by category",
                required=True,
            ),
            MCPToolParameter(
                name="monthly_revenue",
                type="number",
                description="Monthly revenue in dollars",
                required=False,
                default=0,
            ),
        ],
        returns={"type": "object", "properties": {"burn_rate": {"type": "number"}}},
        category="finance",
    )
    server.register_tool(burn_rate_tool, calculate_burn_rate)

    # Register unit economics calculator
    unit_economics_tool = MCPTool(
        name="calculate_unit_economics",
        description="Calculate customer acquisition cost (CAC) and lifetime value (LTV)",
        parameters=[
            MCPToolParameter(
                name="total_marketing_spend",
                type="number",
                description="Total marketing and sales spend",
                required=True,
            ),
            MCPToolParameter(
                name="new_customers",
                type="number",
                description="Number of new customers acquired",
                required=True,
            ),
            MCPToolParameter(
                name="average_revenue_per_customer",
                type="number",
                description="Average revenue per customer per month",
                required=True,
            ),
            MCPToolParameter(
                name="average_customer_lifespan_months",
                type="number",
                description="Average customer lifespan in months",
                required=True,
            ),
            MCPToolParameter(
                name="gross_margin",
                type="number",
                description="Gross margin as a decimal (0-1)",
                required=False,
                default=0.7,
            ),
        ],
        returns={
            "type": "object",
            "properties": {
                "cac": {"type": "number"},
                "ltv": {"type": "number"},
                "ltv_cac_ratio": {"type": "number"},
            },
        },
        category="finance",
    )
    server.register_tool(unit_economics_tool, calculate_unit_economics)

    # Register revenue projection
    revenue_projection_tool = MCPTool(
        name="project_revenue",
        description="Project revenue over time with growth rate",
        parameters=[
            MCPToolParameter(
                name="current_revenue",
                type="number",
                description="Current monthly revenue",
                required=True,
            ),
            MCPToolParameter(
                name="growth_rate",
                type="number",
                description="Monthly growth rate as decimal (e.g., 0.15 for 15%)",
                required=True,
            ),
            MCPToolParameter(
                name="months",
                type="number",
                description="Number of months to project",
                required=False,
                default=12,
            ),
        ],
        returns={
            "type": "object",
            "properties": {
                "projections": {"type": "array"},
                "final_revenue": {"type": "number"},
            },
        },
        category="finance",
    )
    server.register_tool(revenue_projection_tool, project_revenue)

    # Register valuation calculator
    valuation_tool = MCPTool(
        name="calculate_valuation",
        description="Calculate company valuation using multiple methods",
        parameters=[
            MCPToolParameter(
                name="annual_revenue",
                type="number",
                description="Annual recurring revenue",
                required=True,
            ),
            MCPToolParameter(
                name="growth_rate",
                type="number",
                description="Annual growth rate as decimal",
                required=True,
            ),
            MCPToolParameter(
                name="method",
                type="string",
                description="Valuation method",
                required=False,
                default="revenue_multiple",
                enum=["revenue_multiple", "dcf", "market_comp"],
            ),
        ],
        returns={
            "type": "object",
            "properties": {
                "valuation": {"type": "number"},
                "method": {"type": "string"},
            },
        },
        category="finance",
    )
    server.register_tool(valuation_tool, calculate_valuation)

    return server
