"""Personal wealth and salary calculation tools."""

from typing import Any


def optimize_founder_salary(
    company_runway: float,
    company_burn: float,
    personal_expenses: float,
) -> dict[str, Any]:
    """
    Optimize founder salary balancing company and personal needs.

    Args:
        company_runway: Company runway in months
        company_burn: Monthly burn rate
        personal_expenses: Founder's monthly personal expenses

    Returns:
        Salary recommendations
    """
    # Strategy: Pay minimum viable salary that covers essentials
    # Lower salary = longer runway = more flexibility

    # Minimum salary for sustainability
    minimum_monthly = personal_expenses * 0.8  # 80% of expenses

    # Comfortable salary
    comfortable_monthly = personal_expenses * 1.2  # 120% of expenses

    # Conservative recommendation based on runway
    if company_runway < 6:
        # Critical runway - minimize salary
        recommended_monthly = minimum_monthly
        reasoning = "Short runway - minimize salary to extend timeline"
    elif company_runway < 12:
        # Moderate runway - balanced approach
        recommended_monthly = min(comfortable_monthly, personal_expenses)
        reasoning = "Moderate runway - balance personal needs with conservation"
    else:
        # Healthy runway - comfortable salary OK
        recommended_monthly = comfortable_monthly
        reasoning = "Healthy runway - comfortable salary sustainable"

    # Impact on runway
    salary_impact_months = recommended_monthly / company_burn if company_burn > 0 else 0

    return {
        "recommended_monthly": round(recommended_monthly, 2),
        "recommended_annual": round(recommended_monthly * 12, 2),
        "minimum_monthly": round(minimum_monthly, 2),
        "comfortable_monthly": round(comfortable_monthly, 2),
        "salary_as_percentage_of_burn": round(recommended_monthly / company_burn, 4) if company_burn > 0 else 0,
        "runway_impact_months": round(salary_impact_months, 2),
        "reasoning": reasoning,
    }


def calculate_equity_value(
    equity_percentage: float,
    company_valuation: float,
    vesting_months_completed: int,
    vesting_period_months: int = 48,
    cliff_months: int = 12,
) -> dict[str, Any]:
    """
    Calculate equity value and vesting status.

    Args:
        equity_percentage: Founder's equity percentage (e.g., 0.25 for 25%)
        company_valuation: Current company valuation
        vesting_months_completed: Months of vesting completed
        vesting_period_months: Total vesting period (default 4 years)
        cliff_months: Cliff period (default 1 year)

    Returns:
        Equity value and vesting details
    """
    total_equity_value = company_valuation * equity_percentage

    # Calculate vested portion
    if vesting_months_completed < cliff_months:
        vested_percentage = 0
    else:
        vested_percentage = min(1.0, vesting_months_completed / vesting_period_months)

    vested_value = total_equity_value * vested_percentage
    unvested_value = total_equity_value - vested_value

    # Concentration risk (what % of net worth is in company equity)
    # Assuming founder has some other assets
    estimated_liquid_assets = 50000  # Assumption
    total_net_worth = vested_value + estimated_liquid_assets
    concentration_risk = vested_value / total_net_worth if total_net_worth > 0 else 1.0

    return {
        "total_equity_value": round(total_equity_value, 2),
        "equity_percentage": equity_percentage,
        "vested_percentage": round(vested_percentage, 4),
        "vested_value": round(vested_value, 2),
        "unvested_value": round(unvested_value, 2),
        "months_vested": vesting_months_completed,
        "months_remaining": max(0, vesting_period_months - vesting_months_completed),
        "past_cliff": vesting_months_completed >= cliff_months,
        "concentration_risk": round(concentration_risk, 4),
    }


def project_wealth_accumulation(
    annual_salary: float,
    equity_value: float,
    years: int = 5,
    savings_rate: float = 0.3,
    equity_growth_rate: float = 0.5,
    investment_return: float = 0.07,
) -> dict[str, Any]:
    """
    Project wealth accumulation over time.

    Args:
        annual_salary: Annual salary
        equity_value: Current equity value
        years: Years to project
        savings_rate: Percentage of salary saved
        equity_growth_rate: Expected equity growth rate
        investment_return: Expected return on investments

    Returns:
        Wealth projection
    """
    projections = []
    cumulative_savings = 0
    current_equity_value = equity_value

    for year in range(1, years + 1):
        # Salary savings
        annual_savings = annual_salary * savings_rate
        cumulative_savings = cumulative_savings * (1 + investment_return) + annual_savings

        # Equity growth
        current_equity_value = current_equity_value * (1 + equity_growth_rate)

        # Total net worth
        total_net_worth = cumulative_savings + current_equity_value

        projections.append({
            "year": year,
            "salary_savings": round(cumulative_savings, 2),
            "equity_value": round(current_equity_value, 2),
            "total_net_worth": round(total_net_worth, 2),
        })

    return {
        "annual_salary": annual_salary,
        "savings_rate": savings_rate,
        "years": years,
        "projections": projections,
        "final_net_worth": projections[-1]["total_net_worth"] if projections else 0,
        "assumptions": {
            "equity_growth_rate": equity_growth_rate,
            "investment_return": investment_return,
        },
    }


def calculate_exit_scenarios(
    equity_percentage: float,
    exit_valuations: list[float],
    tax_rate: float = 0.20,
) -> dict[str, Any]:
    """
    Calculate after-tax proceeds for different exit scenarios.

    Args:
        equity_percentage: Founder's equity percentage
        exit_valuations: List of potential exit valuations
        tax_rate: Capital gains tax rate

    Returns:
        Exit scenario analysis
    """
    scenarios = []

    for valuation in exit_valuations:
        gross_proceeds = valuation * equity_percentage
        tax_amount = gross_proceeds * tax_rate
        net_proceeds = gross_proceeds - tax_amount

        scenarios.append({
            "exit_valuation": valuation,
            "gross_proceeds": round(gross_proceeds, 2),
            "tax_amount": round(tax_amount, 2),
            "net_proceeds": round(net_proceeds, 2),
            "tax_rate": tax_rate,
        })

    return {
        "equity_percentage": equity_percentage,
        "scenarios": scenarios,
        "tax_optimization_note": "Consider QSBS exemption if eligible (up to $10M tax-free)",
    }
