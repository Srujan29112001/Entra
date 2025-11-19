"""MCP server for tax and policy tools."""

from ..protocol import MCPServer, MCPTool, MCPToolParameter
from app.tools.tax_calculators import (
    calculate_corporate_tax,
    calculate_personal_tax,
    optimize_salary_dividend_split,
    calculate_gst_liability,
)


def create_tax_server() -> MCPServer:
    """Create and configure the Tax & Policy MCP server."""
    server = MCPServer(
        name="tax",
        description="Tax calculations, optimization, and policy compliance",
    )

    # Corporate tax calculator
    server.register_tool(
        MCPTool(
            name="calculate_corporate_tax",
            description="Calculate corporate tax for different jurisdictions",
            parameters=[
                MCPToolParameter(
                    name="taxable_income",
                    type="number",
                    description="Taxable income in local currency",
                    required=True,
                ),
                MCPToolParameter(
                    name="jurisdiction",
                    type="string",
                    description="Tax jurisdiction",
                    required=True,
                    enum=["US", "IN", "UK", "SG", "DE"],
                ),
                MCPToolParameter(
                    name="entity_type",
                    type="string",
                    description="Entity type",
                    required=False,
                    default="private_limited",
                    enum=["private_limited", "llc", "s_corp", "c_corp"],
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "tax_amount": {"type": "number"},
                    "effective_rate": {"type": "number"},
                },
            },
            category="tax",
        ),
        calculate_corporate_tax,
    )

    # Personal tax calculator
    server.register_tool(
        MCPTool(
            name="calculate_personal_tax",
            description="Calculate personal income tax",
            parameters=[
                MCPToolParameter(
                    name="income",
                    type="number",
                    description="Gross income",
                    required=True,
                ),
                MCPToolParameter(
                    name="jurisdiction",
                    type="string",
                    description="Tax jurisdiction",
                    required=True,
                    enum=["US", "IN", "UK", "SG", "DE"],
                ),
                MCPToolParameter(
                    name="deductions",
                    type="number",
                    description="Total deductions",
                    required=False,
                    default=0,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "tax_amount": {"type": "number"},
                    "effective_rate": {"type": "number"},
                },
            },
            category="tax",
        ),
        calculate_personal_tax,
    )

    # Salary-dividend optimizer
    server.register_tool(
        MCPTool(
            name="optimize_salary_dividend_split",
            description="Optimize salary vs dividend split for tax efficiency",
            parameters=[
                MCPToolParameter(
                    name="total_compensation",
                    type="number",
                    description="Total desired compensation",
                    required=True,
                ),
                MCPToolParameter(
                    name="jurisdiction",
                    type="string",
                    description="Tax jurisdiction",
                    required=True,
                    enum=["US", "IN", "UK"],
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "optimal_salary": {"type": "number"},
                    "optimal_dividend": {"type": "number"},
                    "tax_savings": {"type": "number"},
                },
            },
            category="tax",
        ),
        optimize_salary_dividend_split,
    )

    # GST calculator
    server.register_tool(
        MCPTool(
            name="calculate_gst_liability",
            description="Calculate GST/VAT liability",
            parameters=[
                MCPToolParameter(
                    name="gross_revenue",
                    type="number",
                    description="Gross revenue",
                    required=True,
                ),
                MCPToolParameter(
                    name="input_tax_credit",
                    type="number",
                    description="Input tax credit available",
                    required=False,
                    default=0,
                ),
                MCPToolParameter(
                    name="jurisdiction",
                    type="string",
                    description="Tax jurisdiction",
                    required=False,
                    default="IN",
                    enum=["IN", "UK", "EU"],
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "gst_liability": {"type": "number"},
                    "effective_rate": {"type": "number"},
                },
            },
            category="tax",
        ),
        calculate_gst_liability,
    )

    return server
