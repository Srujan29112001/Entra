"""MCP server for personal wealth and salary tools."""

from ..protocol import MCPServer, MCPTool, MCPToolParameter
from app.tools.wealth_calculators import (
    optimize_founder_salary,
    calculate_equity_value,
    project_wealth_accumulation,
)


def create_wealth_server() -> MCPServer:
    """Create and configure the Personal Wealth MCP server."""
    server = MCPServer(
        name="wealth",
        description="Personal wealth planning, salary optimization, and equity management",
    )

    # Founder salary optimizer
    server.register_tool(
        MCPTool(
            name="optimize_founder_salary",
            description="Optimize founder salary based on company runway and personal needs",
            parameters=[
                MCPToolParameter(
                    name="company_cash",
                    type="number",
                    description="Company cash balance",
                    required=True,
                ),
                MCPToolParameter(
                    name="monthly_burn",
                    type="number",
                    description="Company monthly burn rate",
                    required=True,
                ),
                MCPToolParameter(
                    name="personal_expenses",
                    type="number",
                    description="Founder's monthly personal expenses",
                    required=True,
                ),
                MCPToolParameter(
                    name="target_runway_months",
                    type="number",
                    description="Desired runway in months",
                    required=False,
                    default=18,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "recommended_salary": {"type": "number"},
                    "impact_on_runway": {"type": "number"},
                    "alternative_options": {"type": "array"},
                },
            },
            category="wealth",
        ),
        optimize_founder_salary,
    )

    # Equity value calculator
    server.register_tool(
        MCPTool(
            name="calculate_equity_value",
            description="Calculate current equity value and potential outcomes",
            parameters=[
                MCPToolParameter(
                    name="equity_percentage",
                    type="number",
                    description="Equity ownership percentage (0-100)",
                    required=True,
                ),
                MCPToolParameter(
                    name="current_valuation",
                    type="number",
                    description="Current company valuation",
                    required=True,
                ),
                MCPToolParameter(
                    name="vesting_schedule_months",
                    type="number",
                    description="Vesting schedule in months",
                    required=False,
                    default=48,
                ),
                MCPToolParameter(
                    name="cliff_months",
                    type="number",
                    description="Cliff period in months",
                    required=False,
                    default=12,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "current_value": {"type": "number"},
                    "vested_value": {"type": "number"},
                    "unvested_value": {"type": "number"},
                },
            },
            category="wealth",
        ),
        calculate_equity_value,
    )

    # Wealth projection
    server.register_tool(
        MCPTool(
            name="project_wealth_accumulation",
            description="Project personal wealth accumulation over time",
            parameters=[
                MCPToolParameter(
                    name="current_assets",
                    type="number",
                    description="Current total assets",
                    required=True,
                ),
                MCPToolParameter(
                    name="monthly_savings",
                    type="number",
                    description="Monthly savings amount",
                    required=True,
                ),
                MCPToolParameter(
                    name="investment_return_rate",
                    type="number",
                    description="Expected annual investment return (as decimal)",
                    required=False,
                    default=0.07,
                ),
                MCPToolParameter(
                    name="years",
                    type="number",
                    description="Projection period in years",
                    required=False,
                    default=10,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "projections": {"type": "array"},
                    "final_wealth": {"type": "number"},
                },
            },
            category="wealth",
        ),
        project_wealth_accumulation,
    )

    return server
