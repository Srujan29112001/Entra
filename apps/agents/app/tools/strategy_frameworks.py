"""Strategy and market analysis frameworks."""

from typing import Any


def generate_swot_analysis(company_data: dict) -> dict[str, Any]:
    """
    Generate SWOT analysis framework.

    Args:
        company_data: Company information

    Returns:
        SWOT analysis structure
    """
    # In production, use LLM to generate these based on company data
    stage = company_data.get("stage", "seed")
    industry = company_data.get("industry", "")

    return {
        "strengths": [
            "First-mover advantage" if stage == "mvp" else "Established product",
            "Strong technical team",
            "Low burn rate" if company_data.get("monthly_expenses", 0) < 50000 else "Well-funded",
        ],
        "weaknesses": [
            "Limited brand recognition" if stage in ["idea", "mvp"] else "Market penetration",
            "Small team",
            "Limited runway" if company_data.get("runway_months", 12) < 6 else "Resource constraints",
        ],
        "opportunities": [
            f"Growing {industry} market",
            "Digital transformation trends",
            "Expansion to new geographies",
        ],
        "threats": [
            "Intense competition",
            "Market saturation",
            "Economic uncertainty",
        ],
    }


def analyze_market_size(industry: str, geography: str) -> dict[str, Any]:
    """
    Analyze market size (TAM/SAM/SOM).

    Args:
        industry: Industry/vertical
        geography: Target geography

    Returns:
        Market sizing estimates
    """
    # Simplified market data - in production, fetch from market research APIs
    market_data = {
        "saas": {"global": 1000000000000, "us": 400000000000, "in": 50000000000},
        "ecommerce": {"global": 5000000000000, "us": 1000000000000, "in": 100000000000},
        "fintech": {"global": 800000000000, "us": 300000000000, "in": 60000000000},
    }

    industry_key = industry.lower() if industry.lower() in market_data else "saas"
    geo_key = geography.lower() if geography.lower() in ["us", "in", "uk"] else "us"

    tam = market_data[industry_key].get(geo_key, 100000000000)
    sam = tam * 0.1  # Serviceable Addressable Market (10% of TAM)
    som = sam * 0.05  # Serviceable Obtainable Market (5% of SAM)

    return {
        "tam": tam,
        "sam": sam,
        "som": som,
        "industry": industry,
        "geography": geography,
        "methodology": "Top-down market sizing",
    }


def recommend_pricing_strategy(
    product_type: str, target_segment: str
) -> dict[str, Any]:
    """
    Recommend pricing strategy.

    Args:
        product_type: Type of product (saas, ecommerce, etc.)
        target_segment: Target customer segment

    Returns:
        Pricing recommendations
    """
    strategies = {
        "saas": {
            "smb": {
                "model": "Tiered subscription",
                "starting_price": 49,
                "tiers": ["Starter ($49)", "Professional ($99)", "Enterprise ($299)"],
                "billing": "Monthly with annual discount",
            },
            "enterprise": {
                "model": "Usage-based + seats",
                "starting_price": 499,
                "tiers": ["Team ($499)", "Business ($1,999)", "Enterprise (Custom)"],
                "billing": "Annual contract",
            },
        },
        "ecommerce": {
            "smb": {
                "model": "Cost-plus pricing",
                "margin_target": 0.40,
                "strategy": "Competitive pricing with value adds",
            },
        },
    }

    product_key = product_type.lower() if product_type.lower() in strategies else "saas"
    segment_key = target_segment.lower() if target_segment.lower() in ["smb", "enterprise"] else "smb"

    pricing = strategies[product_key].get(segment_key, strategies["saas"]["smb"])

    return {
        "product_type": product_type,
        "target_segment": target_segment,
        "recommended_model": pricing.get("model", "Subscription"),
        "starting_price": pricing.get("starting_price", 99),
        "tiers": pricing.get("tiers", []),
        "billing": pricing.get("billing", "Monthly"),
        "competitive_position": "mid-market",
    }


def generate_gtm_plan(company_data: dict) -> dict[str, Any]:
    """
    Generate Go-to-Market plan.

    Args:
        company_data: Company information

    Returns:
        GTM plan structure
    """
    stage = company_data.get("stage", "seed")
    product_type = company_data.get("product_type", "saas")

    # Distribution channels by product type
    channels = {
        "saas": ["Direct sales", "Content marketing", "SEO/SEM", "Partnerships", "Product-led growth"],
        "ecommerce": ["Marketplace (Amazon)", "Social commerce", "Direct website", "Influencer marketing"],
        "b2b": ["Direct sales", "Channel partners", "Trade shows", "LinkedIn ads"],
    }

    recommended_channels = channels.get(product_type, channels["saas"])

    return {
        "primary_channels": recommended_channels[:3],
        "customer_acquisition_strategy": "Inbound marketing + targeted outbound",
        "launch_phases": [
            {"phase": "Beta", "duration": "2 months", "goal": "Product validation"},
            {"phase": "Launch", "duration": "3 months", "goal": "Initial traction"},
            {"phase": "Scale", "duration": "6+ months", "goal": "Rapid growth"},
        ],
        "key_metrics": ["CAC", "LTV", "Conversion rate", "Churn rate"],
    }
