"""Tax calculation tools."""

from typing import Any


# Tax rates by country (simplified - in production, use detailed tax tables)
TAX_RATES = {
    "US": {
        "corporate": 0.21,
        "personal_brackets": [(0, 11000, 0.10), (11000, 44725, 0.12), (44725, 95375, 0.22)],
        "dividend_rate": 0.15,
    },
    "IN": {
        "corporate": 0.25,  # For companies < 400Cr turnover
        "personal_brackets": [(0, 250000, 0.0), (250000, 500000, 0.05), (500000, 1000000, 0.20)],
        "dividend_rate": 0.10,
    },
    "UK": {
        "corporate": 0.19,
        "personal_brackets": [(0, 12570, 0.0), (12570, 50270, 0.20), (50270, 150000, 0.40)],
        "dividend_rate": 0.075,
    },
}


def calculate_corporate_tax(income: float, country: str = "US") -> dict[str, Any]:
    """
    Calculate corporate tax.

    Args:
        income: Annual corporate income/profit
        country: Country code

    Returns:
        Tax calculation details
    """
    rates = TAX_RATES.get(country, TAX_RATES["US"])
    corporate_rate = rates["corporate"]

    tax_amount = income * corporate_rate
    after_tax_income = income - tax_amount

    return {
        "income": income,
        "tax_rate": corporate_rate,
        "tax_amount": round(tax_amount, 2),
        "after_tax_income": round(after_tax_income, 2),
        "effective_rate": corporate_rate,
        "country": country,
    }


def calculate_personal_tax(income: float, country: str = "US") -> dict[str, Any]:
    """
    Calculate personal income tax using brackets.

    Args:
        income: Annual personal income
        country: Country code

    Returns:
        Tax calculation details
    """
    rates = TAX_RATES.get(country, TAX_RATES["US"])
    brackets = rates["personal_brackets"]

    total_tax = 0
    remaining_income = income
    current_bracket = None

    for lower, upper, rate in brackets:
        if remaining_income <= 0:
            break

        taxable_in_bracket = min(remaining_income, upper - lower)
        tax_in_bracket = taxable_in_bracket * rate
        total_tax += tax_in_bracket
        remaining_income -= taxable_in_bracket
        current_bracket = rate

    # Tax on remaining income (highest bracket)
    if remaining_income > 0 and current_bracket is not None:
        total_tax += remaining_income * current_bracket

    effective_rate = total_tax / income if income > 0 else 0

    return {
        "income": income,
        "tax_amount": round(total_tax, 2),
        "after_tax_income": round(income - total_tax, 2),
        "effective_rate": round(effective_rate, 4),
        "bracket": "highest" if remaining_income > 0 else "middle",
        "country": country,
    }


def optimize_salary_dividend_split(
    total_amount: float, country: str = "US"
) -> dict[str, Any]:
    """
    Optimize salary vs dividend split for tax efficiency.

    Args:
        total_amount: Total amount founder wants to withdraw
        country: Country code

    Returns:
        Optimal split recommendation
    """
    rates = TAX_RATES.get(country, TAX_RATES["US"])

    # Strategy: Pay minimum salary for social security, rest as dividends
    # (Simplified - in reality, more complex)

    if country == "US":
        # Reasonable salary for S-Corp
        recommended_salary = min(total_amount * 0.4, 160000)
    elif country == "IN":
        # Higher salary often better in India
        recommended_salary = total_amount * 0.6
    else:
        recommended_salary = total_amount * 0.5

    recommended_dividend = total_amount - recommended_salary

    # Calculate taxes for this split
    salary_tax = calculate_personal_tax(recommended_salary, country)
    dividend_tax = recommended_dividend * rates.get("dividend_rate", 0.15)

    total_tax = salary_tax["tax_amount"] + dividend_tax
    net_amount = total_amount - total_tax

    return {
        "total_amount": total_amount,
        "recommended_salary": round(recommended_salary, 2),
        "recommended_dividend": round(recommended_dividend, 2),
        "salary_tax": salary_tax["tax_amount"],
        "dividend_tax": round(dividend_tax, 2),
        "total_tax": round(total_tax, 2),
        "net_amount": round(net_amount, 2),
        "effective_rate": round(total_tax / total_amount, 4),
        "strategy": "Optimize salary/dividend split for tax efficiency",
    }


def calculate_gst_liability(
    revenue: float, expenses: float, country: str = "IN"
) -> dict[str, Any]:
    """
    Calculate GST/VAT liability.

    Args:
        revenue: Annual revenue
        expenses: Annual expenses (with GST)
        country: Country code

    Returns:
        GST calculation
    """
    if country == "IN":
        gst_rate = 0.18  # Standard GST rate
        output_gst = revenue * gst_rate
        input_gst = expenses * gst_rate  # Simplified
        net_gst = output_gst - input_gst
    elif country == "UK":
        vat_rate = 0.20
        output_gst = revenue * vat_rate
        input_gst = expenses * vat_rate
        net_gst = output_gst - input_gst
    else:
        return {"applicable": False, "country": country}

    return {
        "applicable": True,
        "revenue": revenue,
        "expenses": expenses,
        "output_tax": round(output_gst, 2),
        "input_tax_credit": round(input_gst, 2),
        "net_liability": round(net_gst, 2),
        "rate": gst_rate if country == "IN" else vat_rate,
        "country": country,
    }
