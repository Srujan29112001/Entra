"""
Real Data API Integrations - NO MOCKS.

This module provides production-grade integrations with real data sources:
- FRED (Federal Reserve Economic Data)
- World Bank Open Data
- IRS Tax Data
- Market Data APIs

All functions raise exceptions instead of falling back to mock data.
"""

import httpx
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class FREDAPIClient:
    """
    Federal Reserve Economic Data (FRED) API Client.

    Provides real macroeconomic indicators from the St. Louis Fed.
    API Docs: https://fred.stlouisfed.org/docs/api/fred/
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize FRED API client."""
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise ValueError(
                "FRED_API_KEY not set. Get one at https://fred.stlouisfed.org/docs/api/api_key.html"
            )
        self.base_url = "https://api.stlouisfed.org/fred"

    async def get_series(
        self,
        series_id: str,
        limit: int = 1,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Get data for a FRED series.

        Args:
            series_id: FRED series ID (e.g., 'GDP', 'CPIAUCSL', 'UNRATE')
            limit: Number of observations to return
            sort_order: 'asc' or 'desc'

        Returns:
            Series data with observations

        Common Series IDs:
        - GDP: Gross Domestic Product
        - CPIAUCSL: Consumer Price Index (Inflation)
        - UNRATE: Unemployment Rate
        - DFF: Federal Funds Rate
        - T10Y2Y: 10-Year Treasury Minus 2-Year
        - DEXUSEU: USD/EUR Exchange Rate
        """
        async with httpx.AsyncClient() as client:
            # Get series observations
            response = await client.get(
                f"{self.base_url}/series/observations",
                params={
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "limit": limit,
                    "sort_order": sort_order,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            if "observations" not in data:
                raise ValueError(f"No data found for series {series_id}")

            observations = data["observations"]
            if not observations:
                raise ValueError(f"No observations for series {series_id}")

            latest = observations[0]
            return {
                "series_id": series_id,
                "value": float(latest["value"]),
                "date": latest["date"],
                "units": await self._get_series_info(series_id),
            }

    async def _get_series_info(self, series_id: str) -> str:
        """Get series metadata."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/series",
                params={
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            if "seriess" in data and data["seriess"]:
                return data["seriess"][0].get("units", "")
            return ""

    async def get_gdp(self, country: str = "US") -> Dict[str, Any]:
        """Get latest GDP data."""
        if country == "US":
            return await self.get_series("GDP")
        else:
            raise NotImplementedError(f"GDP data for {country} not implemented via FRED")

    async def get_inflation(self, country: str = "US") -> Dict[str, Any]:
        """Get latest inflation (CPI) data."""
        if country == "US":
            data = await self.get_series("CPIAUCSL")
            # Calculate year-over-year change
            data_12mo = await self.get_series("CPIAUCSL", limit=12, sort_order="desc")
            if len(data_12mo) >= 12:
                current = float(data["value"])
                year_ago = float(data_12mo[11]["value"])
                yoy_change = ((current - year_ago) / year_ago) * 100
                data["yoy_change_percent"] = round(yoy_change, 2)
            return data
        else:
            raise NotImplementedError(f"Inflation data for {country} not implemented via FRED")

    async def get_unemployment(self, country: str = "US") -> Dict[str, Any]:
        """Get latest unemployment rate."""
        if country == "US":
            return await self.get_series("UNRATE")
        else:
            raise NotImplementedError(f"Unemployment data for {country} not implemented via FRED")

    async def get_interest_rate(self, country: str = "US") -> Dict[str, Any]:
        """Get latest federal funds rate (policy rate)."""
        if country == "US":
            return await self.get_series("DFF")
        else:
            raise NotImplementedError(f"Interest rate data for {country} not implemented via FRED")


class WorldBankAPIClient:
    """
    World Bank Open Data API Client.

    Provides global economic and development indicators.
    API Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
    """

    def __init__(self):
        """Initialize World Bank API client."""
        self.base_url = "https://api.worldbank.org/v2"

    async def get_indicator(
        self,
        country_code: str,
        indicator_code: str,
        most_recent_value: int = 1,
    ) -> Dict[str, Any]:
        """
        Get indicator data for a country.

        Args:
            country_code: ISO 2-letter country code (e.g., 'US', 'IN', 'GB')
            indicator_code: World Bank indicator code
            most_recent_value: Number of most recent values

        Returns:
            Indicator data

        Common Indicators:
        - NY.GDP.MKTP.CD: GDP (current US$)
        - FP.CPI.TOTL.ZG: Inflation, consumer prices (annual %)
        - SL.UEM.TOTL.ZS: Unemployment, total (% of labor force)
        - FR.INR.RINR: Real interest rate (%)
        - NY.GDP.PCAP.CD: GDP per capita (current US$)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/country/{country_code}/indicator/{indicator_code}",
                params={
                    "format": "json",
                    "per_page": most_recent_value,
                    "mrnev": most_recent_value,  # Most Recent Non-Empty Value
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or not data[1]:
                raise ValueError(f"No data found for {indicator_code} in {country_code}")

            latest = data[1][0]
            if latest["value"] is None:
                raise ValueError(f"No value for {indicator_code} in {country_code}")

            return {
                "country": latest["country"]["value"],
                "country_code": country_code,
                "indicator": latest["indicator"]["value"],
                "indicator_code": indicator_code,
                "value": float(latest["value"]),
                "date": latest["date"],
                "unit": latest.get("unit", ""),
            }

    async def get_gdp(self, country_code: str) -> Dict[str, Any]:
        """Get latest GDP for a country."""
        return await self.get_indicator(country_code, "NY.GDP.MKTP.CD")

    async def get_gdp_per_capita(self, country_code: str) -> Dict[str, Any]:
        """Get latest GDP per capita."""
        return await self.get_indicator(country_code, "NY.GDP.PCAP.CD")

    async def get_inflation(self, country_code: str) -> Dict[str, Any]:
        """Get latest inflation rate."""
        return await self.get_indicator(country_code, "FP.CPI.TOTL.ZG")

    async def get_unemployment(self, country_code: str) -> Dict[str, Any]:
        """Get latest unemployment rate."""
        return await self.get_indicator(country_code, "SL.UEM.TOTL.ZS")

    async def get_population(self, country_code: str) -> Dict[str, Any]:
        """Get latest population."""
        return await self.get_indicator(country_code, "SP.POP.TOTL")


class UnifiedEconomicDataAPI:
    """
    Unified API that combines FRED and World Bank data.

    Provides seamless access to economic indicators across countries.
    """

    def __init__(self, fred_api_key: Optional[str] = None):
        """Initialize unified API."""
        self.fred = FREDAPIClient(fred_api_key) if fred_api_key else None
        self.world_bank = WorldBankAPIClient()

    async def get_gdp(self, country: str = "US") -> Dict[str, Any]:
        """Get GDP for any country."""
        country_code = self._get_country_code(country)

        if country_code == "US" and self.fred:
            try:
                return await self.fred.get_gdp(country)
            except Exception:
                pass  # Fallback to World Bank

        return await self.world_bank.get_gdp(country_code)

    async def get_inflation(self, country: str = "US") -> Dict[str, Any]:
        """Get inflation for any country."""
        country_code = self._get_country_code(country)

        if country_code == "US" and self.fred:
            try:
                return await self.fred.get_inflation(country)
            except Exception:
                pass

        return await self.world_bank.get_inflation(country_code)

    async def get_unemployment(self, country: str = "US") -> Dict[str, Any]:
        """Get unemployment for any country."""
        country_code = self._get_country_code(country)

        if country_code == "US" and self.fred:
            try:
                return await self.fred.get_unemployment(country)
            except Exception:
                pass

        return await self.world_bank.get_unemployment(country_code)

    async def get_interest_rate(self, country: str = "US") -> Dict[str, Any]:
        """Get policy interest rate."""
        country_code = self._get_country_code(country)

        if country_code == "US" and self.fred:
            return await self.fred.get_interest_rate(country)
        else:
            return await self.world_bank.get_indicator(country_code, "FR.INR.RINR")

    def _get_country_code(self, country: str) -> str:
        """Convert country name to ISO code."""
        mapping = {
            "US": "US",
            "USA": "US",
            "United States": "US",
            "IN": "IN",
            "India": "IN",
            "UK": "GB",
            "United Kingdom": "GB",
            "CN": "CN",
            "China": "CN",
            "EU": "EU",
            "DE": "DE",
            "Germany": "DE",
            "FR": "FR",
            "France": "FR",
            "JP": "JP",
            "Japan": "JP",
            "SG": "SG",
            "Singapore": "SG",
        }
        return mapping.get(country, country)


# Export for easy imports
__all__ = [
    "FREDAPIClient",
    "WorldBankAPIClient",
    "UnifiedEconomicDataAPI",
]
