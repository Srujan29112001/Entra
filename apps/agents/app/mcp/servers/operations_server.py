"""MCP Server for Operations tools."""

from app.mcp.protocol import MCPServer, MCPTool, MCPToolParameter
from typing import Dict, Any, List


def create_operations_server() -> MCPServer:
    """Create and configure the Operations MCP server."""
    server = MCPServer(
        name="operations_server",
        description="Tools for operational planning, pricing, team planning, and resource allocation",
    )

    # Tool 1: Pricing Optimizer
    pricing_tool = MCPTool(
        name="optimize_pricing",
        description="Analyze and optimize product pricing based on costs and targets",
        parameters=[
            MCPToolParameter(
                name="cost_per_unit",
                type="number",
                description="Cost to deliver one unit (COGS)",
                required=True,
            ),
            MCPToolParameter(
                name="target_margin",
                type="number",
                description="Target gross margin (e.g., 0.7 for 70%)",
                required=True,
            ),
            MCPToolParameter(
                name="market_price",
                type="number",
                description="Current market/competitor price",
                required=False,
            ),
        ],
        returns={"type": "object"},
        category="operations",
    )

    async def optimize_pricing_handler(
        cost_per_unit: float,
        target_margin: float,
        market_price: float = None,
    ) -> Dict[str, Any]:
        """Calculate optimal pricing."""
        # Calculate cost-plus price
        cost_plus_price = cost_per_unit / (1 - target_margin)

        # Calculate margin at different price points
        price_scenarios = []

        # Test prices from 0.8x to 1.5x of cost-plus
        for multiplier in [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]:
            price = cost_plus_price * multiplier
            margin = (price - cost_per_unit) / price if price > 0 else 0
            profit_per_unit = price - cost_per_unit

            price_scenarios.append({
                "price": round(price, 2),
                "margin": round(margin, 3),
                "margin_percent": round(margin * 100, 1),
                "profit_per_unit": round(profit_per_unit, 2),
            })

        result = {
            "cost_per_unit": cost_per_unit,
            "target_margin": target_margin,
            "recommended_price": round(cost_plus_price, 2),
            "price_scenarios": price_scenarios,
        }

        # Compare to market if provided
        if market_price:
            market_margin = (market_price - cost_per_unit) / market_price if market_price > 0 else 0
            result["market_comparison"] = {
                "market_price": market_price,
                "market_margin": round(market_margin, 3),
                "price_difference_percent": round(
                    ((cost_plus_price / market_price) - 1) * 100, 1
                ) if market_price > 0 else 0,
                "competitive_position": (
                    "premium" if cost_plus_price > market_price * 1.1
                    else "discount" if cost_plus_price < market_price * 0.9
                    else "at market"
                ),
            }

        return result

    server.register_tool(pricing_tool, optimize_pricing_handler)

    # Tool 2: Team Capacity Planner
    team_planner_tool = MCPTool(
        name="plan_team_capacity",
        description="Plan team size and hiring based on revenue and workload",
        parameters=[
            MCPToolParameter(
                name="monthly_revenue",
                type="number",
                description="Current monthly revenue",
                required=True,
            ),
            MCPToolParameter(
                name="current_team_size",
                type="number",
                description="Current number of employees",
                required=True,
            ),
            MCPToolParameter(
                name="growth_rate",
                type="number",
                description="Monthly growth rate (e.g., 0.1 for 10%)",
                required=True,
            ),
            MCPToolParameter(
                name="months_ahead",
                type="number",
                description="Months to plan ahead",
                required=False,
                default=12,
            ),
        ],
        returns={"type": "object"},
        category="operations",
    )

    async def plan_team_capacity_handler(
        monthly_revenue: float,
        current_team_size: int,
        growth_rate: float,
        months_ahead: int = 12,
    ) -> Dict[str, Any]:
        """Plan team hiring based on growth."""
        # Benchmark: $15K MRR per employee for SaaS
        target_revenue_per_employee = 15000

        projections = []
        for month in range(months_ahead + 1):
            # Project revenue
            projected_revenue = monthly_revenue * ((1 + growth_rate) ** month)

            # Calculate needed team size
            optimal_team_size = max(
                current_team_size,
                int(projected_revenue / target_revenue_per_employee)
            )

            # Current revenue per employee
            revenue_per_employee = (
                projected_revenue / optimal_team_size if optimal_team_size > 0 else 0
            )

            projections.append({
                "month": month,
                "projected_revenue": round(projected_revenue, 2),
                "recommended_team_size": optimal_team_size,
                "revenue_per_employee": round(revenue_per_employee, 2),
            })

        # Calculate hiring plan
        final_team_size = projections[-1]["recommended_team_size"]
        total_hires = max(0, final_team_size - current_team_size)

        return {
            "current_team_size": current_team_size,
            "current_revenue": monthly_revenue,
            "projected_team_size": final_team_size,
            "total_hires_needed": total_hires,
            "hiring_timeline": projections,
            "recommendations": {
                "hire_per_quarter": round(total_hires / 4, 1),
                "target_revenue_per_employee": target_revenue_per_employee,
            },
        }

    server.register_tool(team_planner_tool, plan_team_capacity_handler)

    # Tool 3: Salary Budget Calculator
    salary_budget_tool = MCPTool(
        name="calculate_salary_budget",
        description="Calculate salary budget based on roles and market rates",
        parameters=[
            MCPToolParameter(
                name="roles",
                type="array",
                description="List of roles with counts",
                required=True,
            ),
            MCPToolParameter(
                name="country",
                type="string",
                description="Country for salary benchmarks",
                required=True,
            ),
            MCPToolParameter(
                name="adjustment_factor",
                type="number",
                description="Adjustment for company (e.g., 0.9 for 10% below market)",
                required=False,
                default=1.0,
            ),
        ],
        returns={"type": "object"},
        category="operations",
    )

    async def calculate_salary_budget_handler(
        roles: List[Dict[str, Any]],
        country: str,
        adjustment_factor: float = 1.0,
    ) -> Dict[str, Any]:
        """Calculate total salary budget."""
        # Simplified salary benchmarks (monthly, in USD)
        benchmarks = {
            "US": {
                "engineer": 12000,
                "senior_engineer": 18000,
                "designer": 10000,
                "product_manager": 14000,
                "sales": 8000,
                "marketing": 7000,
                "ops": 6000,
            },
            "IN": {
                "engineer": 2500,
                "senior_engineer": 4500,
                "designer": 2000,
                "product_manager": 3500,
                "sales": 2000,
                "marketing": 1800,
                "ops": 1500,
            },
            "UK": {
                "engineer": 9000,
                "senior_engineer": 14000,
                "designer": 7500,
                "product_manager": 11000,
                "sales": 6500,
                "marketing": 6000,
                "ops": 5000,
            },
        }

        country_benchmarks = benchmarks.get(country, benchmarks["US"])

        role_budgets = []
        total_monthly = 0
        total_annual = 0

        for role_spec in roles:
            role_type = role_spec.get("type", "engineer")
            count = role_spec.get("count", 1)

            base_salary = country_benchmarks.get(role_type, 5000)
            adjusted_salary = base_salary * adjustment_factor

            monthly_cost = adjusted_salary * count
            annual_cost = monthly_cost * 12

            total_monthly += monthly_cost
            total_annual += annual_cost

            role_budgets.append({
                "role": role_type,
                "count": count,
                "monthly_per_person": round(adjusted_salary, 2),
                "monthly_total": round(monthly_cost, 2),
                "annual_total": round(annual_cost, 2),
            })

        return {
            "country": country,
            "adjustment_factor": adjustment_factor,
            "role_budgets": role_budgets,
            "total_monthly_budget": round(total_monthly, 2),
            "total_annual_budget": round(total_annual, 2),
            "total_headcount": sum(r.get("count", 0) for r in roles),
        }

    server.register_tool(salary_budget_tool, calculate_salary_budget_handler)

    return server
