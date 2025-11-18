"""Tests for calculation tools."""

from app.tools.financial_calculators import (
    calculate_runway,
    calculate_burn_rate,
    calculate_unit_economics,
)
from app.tools.tax_calculators import calculate_corporate_tax, optimize_salary_dividend_split
from app.tools.wealth_calculators import optimize_founder_salary, calculate_equity_value


def test_calculate_runway():
    """Test runway calculation."""
    runway = calculate_runway(cash_balance=100000, monthly_burn=10000)
    assert runway == 10.0

    # Infinite runway if profitable
    runway = calculate_runway(cash_balance=100000, monthly_burn=-5000)
    assert runway == float("inf")


def test_calculate_burn_rate():
    """Test burn rate calculation."""
    burn = calculate_burn_rate(monthly_revenue=20000, monthly_expenses=15000)
    assert burn == -5000  # Profitable

    burn = calculate_burn_rate(monthly_revenue=10000, monthly_expenses=15000)
    assert burn == 5000  # Burning


def test_calculate_unit_economics():
    """Test unit economics."""
    result = calculate_unit_economics(cac=500, ltv=2000)

    assert result["ltv_cac_ratio"] == 4.0
    assert result["healthy"] is True

    # Unhealthy
    result = calculate_unit_economics(cac=1000, ltv=2000)
    assert result["ltv_cac_ratio"] == 2.0
    assert result["healthy"] is False


def test_corporate_tax_calculation():
    """Test corporate tax calculation."""
    result = calculate_corporate_tax(income=100000, country="US")

    assert result["income"] == 100000
    assert result["tax_rate"] == 0.21
    assert result["tax_amount"] == 21000
    assert result["after_tax_income"] == 79000


def test_salary_dividend_optimization():
    """Test salary vs dividend optimization."""
    result = optimize_salary_dividend_split(total_amount=100000, country="US")

    assert result["total_amount"] == 100000
    assert result["recommended_salary"] + result["recommended_dividend"] == 100000
    assert result["total_tax"] > 0


def test_founder_salary_optimization():
    """Test founder salary optimization."""
    result = optimize_founder_salary(
        company_runway=12, company_burn=10000, personal_expenses=5000
    )

    assert result["recommended_monthly"] > 0
    assert result["recommended_monthly"] <= 6000  # Should be conservative


def test_equity_value_calculation():
    """Test equity value calculation."""
    result = calculate_equity_value(
        equity_percentage=0.25,
        company_valuation=10000000,
        vesting_months_completed=24,
        vesting_period_months=48,
    )

    assert result["total_equity_value"] == 2500000
    assert result["vested_percentage"] == 0.5
    assert result["vested_value"] == 1250000
    assert result["unvested_value"] == 1250000
    assert result["past_cliff"] is True
