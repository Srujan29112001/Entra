"""MCP Server for Investor Relations tools."""

from app.mcp.protocol import MCPServer, MCPTool, MCPToolParameter
from typing import Dict, Any


def create_investor_server() -> MCPServer:
    """Create and configure the Investor Relations MCP server."""
    server = MCPServer(
        name="investor_server",
        description="Tools for investor relations, fundraising, and pitch preparation",
    )

    # Tool 1: Funding Calculator
    funding_calculator_tool = MCPTool(
        name="calculate_funding_needs",
        description="Calculate funding needs based on burn rate and runway targets",
        parameters=[
            MCPToolParameter(
                name="monthly_burn",
                type="number",
                description="Monthly burn rate in dollars",
                required=True,
            ),
            MCPToolParameter(
                name="current_runway_months",
                type="number",
                description="Current runway in months",
                required=True,
            ),
            MCPToolParameter(
                name="target_runway_months",
                type="number",
                description="Target runway after fundraise (default 18)",
                required=False,
                default=18,
            ),
            MCPToolParameter(
                name="growth_buffer_percent",
                type="number",
                description="Buffer percentage for growth (default 30%)",
                required=False,
                default=0.3,
            ),
        ],
        returns={"type": "object"},
        category="investor",
    )

    async def calculate_funding_needs_handler(
        monthly_burn: float,
        current_runway_months: float,
        target_runway_months: float = 18,
        growth_buffer_percent: float = 0.3,
    ) -> Dict[str, Any]:
        """Calculate how much funding to raise."""
        # Calculate months needed
        months_deficit = max(0, target_runway_months - current_runway_months)

        # Base funding need
        base_funding = monthly_burn * months_deficit

        # Add growth buffer
        growth_buffer = base_funding * growth_buffer_percent
        total_raise = base_funding + growth_buffer

        return {
            "base_funding_need": round(base_funding, 2),
            "growth_buffer": round(growth_buffer, 2),
            "recommended_raise": round(total_raise, 2),
            "current_runway_months": current_runway_months,
            "target_runway_months": target_runway_months,
            "runway_after_raise": round(current_runway_months + (total_raise / monthly_burn), 1),
        }

    server.register_tool(funding_calculator_tool, calculate_funding_needs_handler)

    # Tool 2: Valuation Estimator
    valuation_tool = MCPTool(
        name="estimate_valuation",
        description="Estimate startup valuation using revenue multiples",
        parameters=[
            MCPToolParameter(
                name="arr",
                type="number",
                description="Annual Recurring Revenue",
                required=True,
            ),
            MCPToolParameter(
                name="growth_rate",
                type="number",
                description="YoY growth rate (e.g., 1.5 for 150%)",
                required=True,
            ),
            MCPToolParameter(
                name="stage",
                type="string",
                description="Funding stage",
                required=True,
                enum=["pre_seed", "seed", "series_a", "series_b"],
            ),
        ],
        returns={"type": "object"},
        category="investor",
    )

    async def estimate_valuation_handler(
        arr: float,
        growth_rate: float,
        stage: str,
    ) -> Dict[str, Any]:
        """Estimate valuation based on revenue multiples."""
        # Revenue multiples by stage (industry benchmarks)
        multiples = {
            "pre_seed": (2, 5),  # 2-5x ARR
            "seed": (3, 8),  # 3-8x ARR
            "series_a": (5, 12),  # 5-12x ARR
            "series_b": (8, 15),  # 8-15x ARR
        }

        base_multiple_low, base_multiple_high = multiples.get(stage, (3, 8))

        # Adjust for growth rate
        if growth_rate > 2.0:  # >200% growth
            base_multiple_low *= 1.5
            base_multiple_high *= 1.5
        elif growth_rate < 0.5:  # <50% growth
            base_multiple_low *= 0.7
            base_multiple_high *= 0.7

        valuation_low = arr * base_multiple_low
        valuation_high = arr * base_multiple_high
        valuation_mid = (valuation_low + valuation_high) / 2

        return {
            "arr": arr,
            "growth_rate": growth_rate,
            "stage": stage,
            "valuation_range": {
                "low": round(valuation_low, 2),
                "mid": round(valuation_mid, 2),
                "high": round(valuation_high, 2),
            },
            "multiples_used": {
                "low": round(base_multiple_low, 1),
                "high": round(base_multiple_high, 1),
            },
        }

    server.register_tool(valuation_tool, estimate_valuation_handler)

    # Tool 3: Investor Type Matcher
    investor_matcher_tool = MCPTool(
        name="match_investor_types",
        description="Recommend investor types based on stage and metrics",
        parameters=[
            MCPToolParameter(
                name="stage",
                type="string",
                description="Company stage",
                required=True,
                enum=["idea", "mvp", "seed", "series_a", "series_b", "growth"],
            ),
            MCPToolParameter(
                name="raise_amount",
                type="number",
                description="Amount looking to raise",
                required=True,
            ),
        ],
        returns={"type": "object"},
        category="investor",
    )

    async def match_investor_types_handler(
        stage: str,
        raise_amount: float,
    ) -> Dict[str, Any]:
        """Match company to appropriate investor types."""
        investor_types = []

        # Based on raise amount and stage
        if raise_amount < 250000:
            investor_types.extend([
                {"type": "Angel Investors", "typical_check": "10K-50K", "priority": "High"},
                {"type": "Friends & Family", "typical_check": "5K-25K", "priority": "High"},
                {"type": "Micro VCs", "typical_check": "25K-100K", "priority": "Medium"},
            ])
        elif raise_amount < 1500000:
            investor_types.extend([
                {"type": "Seed VCs", "typical_check": "100K-500K", "priority": "High"},
                {"type": "Angel Groups", "typical_check": "50K-250K", "priority": "High"},
                {"type": "Accelerators", "typical_check": "25K-150K", "priority": "Medium"},
            ])
        elif raise_amount < 5000000:
            investor_types.extend([
                {"type": "Early-stage VCs", "typical_check": "500K-2M", "priority": "High"},
                {"type": "Corporate VCs", "typical_check": "250K-1M", "priority": "Medium"},
                {"type": "Family Offices", "typical_check": "250K-1M", "priority": "Medium"},
            ])
        else:
            investor_types.extend([
                {"type": "Growth VCs", "typical_check": "2M-10M", "priority": "High"},
                {"type": "Private Equity", "typical_check": "5M-20M", "priority": "Medium"},
                {"type": "Corporate VCs", "typical_check": "1M-5M", "priority": "Medium"},
            ])

        return {
            "stage": stage,
            "raise_amount": raise_amount,
            "recommended_investors": investor_types,
            "typical_round_size": f"${raise_amount:,.0f}",
        }

    server.register_tool(investor_matcher_tool, match_investor_types_handler)

    return server
