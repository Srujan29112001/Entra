"""Financial calculation tools."""

from typing import Any


def calculate_runway(cash_balance: float, monthly_burn: float) -> float:
    """
    Calculate runway in months.

    Args:
        cash_balance: Current cash balance
        monthly_burn: Monthly burn rate (expenses - revenue)

    Returns:
        Runway in months
    """
    if monthly_burn <= 0:
        return float("inf")
    return cash_balance / monthly_burn


def calculate_burn_rate(monthly_revenue: float, monthly_expenses: float) -> float:
    """
    Calculate monthly burn rate.

    Args:
        monthly_revenue: Monthly revenue
        monthly_expenses: Monthly expenses

    Returns:
        Monthly burn rate (negative = profit)
    """
    return monthly_expenses - monthly_revenue


def calculate_unit_economics(cac: float, ltv: float) -> dict[str, Any]:
    """
    Calculate unit economics metrics.

    Args:
        cac: Customer Acquisition Cost
        ltv: Lifetime Value

    Returns:
        Dictionary with unit economics metrics
    """
    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    payback_months = cac / (ltv / 12) if ltv > 0 else float("inf")

    return {
        "cac": cac,
        "ltv": ltv,
        "ltv_cac_ratio": ltv_cac_ratio,
        "payback_months": payback_months,
        "healthy": ltv_cac_ratio >= 3,
    }


def project_revenue(
    current_revenue: float, growth_rate: float, months: int = 12
) -> list[dict[str, Any]]:
    """
    Project revenue growth.

    Args:
        current_revenue: Current monthly revenue
        growth_rate: Monthly growth rate (e.g., 0.1 for 10%)
        months: Number of months to project

    Returns:
        List of monthly projections
    """
    projections = []
    revenue = current_revenue

    for month in range(1, months + 1):
        revenue = revenue * (1 + growth_rate)
        projections.append({"month": month, "revenue": round(revenue, 2)})

    return projections


def calculate_valuation(
    revenue: float,
    growth_rate: float,
    stage: str,
) -> dict[str, Any]:
    """
    Estimate company valuation using revenue multiples.

    Args:
        revenue: Annual recurring revenue
        growth_rate: YoY growth rate
        stage: Company stage (seed, series_a, etc.)

    Returns:
        Valuation estimate
    """
    # Industry-standard multiples by stage
    multiples = {
        "seed": 5,
        "series_a": 8,
        "series_b": 12,
        "growth": 15,
    }

    base_multiple = multiples.get(stage, 5)

    # Adjust for growth
    if growth_rate > 1.0:  # >100% YoY
        growth_multiplier = 1.5
    elif growth_rate > 0.5:  # >50% YoY
        growth_multiplier = 1.2
    else:
        growth_multiplier = 1.0

    valuation = revenue * base_multiple * growth_multiplier

    return {
        "valuation": round(valuation, 2),
        "revenue": revenue,
        "multiple": base_multiple * growth_multiplier,
        "methodology": "Revenue multiple",
    }


def calculate_option_pool(
    total_shares: int, pool_percentage: float, pre_or_post: str = "post"
) -> dict[str, Any]:
    """
    Calculate ESOP pool dilution.

    Args:
        total_shares: Total shares outstanding
        pool_percentage: Option pool as percentage (e.g., 0.15 for 15%)
        pre_or_post: Whether pool is pre-money or post-money

    Returns:
        Option pool calculations
    """
    if pre_or_post == "post":
        pool_shares = int(total_shares * pool_percentage)
        founder_dilution = 0  # No dilution if post-money
    else:
        pool_shares = int(total_shares * pool_percentage / (1 - pool_percentage))
        founder_dilution = pool_percentage

    return {
        "pool_shares": pool_shares,
        "pool_percentage": pool_percentage,
        "founder_dilution": founder_dilution,
        "pre_or_post": pre_or_post,
    }
