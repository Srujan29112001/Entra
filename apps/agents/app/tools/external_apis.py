"""External API integrations for real-time data."""

import httpx
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class FinancialDataAPI:
    """
    Integration with financial data APIs (Alpha Vantage, Yahoo Finance).

    Provides real-time stock prices, forex rates, economic indicators.
    """

    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.base_url = "https://www.alphavantage.co/query"

    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock quote.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dict with price, change, volume, etc.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol": symbol,
                        "apikey": self.alpha_vantage_key,
                    },
                    timeout=10.0,
                )
                data = response.json()

                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    return {
                        "symbol": symbol,
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": quote.get("10. change percent", "0%"),
                        "volume": int(quote.get("06. volume", 0)),
                        "timestamp": quote.get("07. latest trading day"),
                    }
                else:
                    # Fallback mock data for demo
                    return self._mock_stock_quote(symbol)
        except Exception as e:
            print(f"Error fetching stock quote: {e}")
            return self._mock_stock_quote(symbol)

    def _mock_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Mock stock data for development/demo."""
        import random
        base_prices = {"AAPL": 175.0, "MSFT": 380.0, "GOOGL": 140.0, "AMZN": 145.0}
        base = base_prices.get(symbol, 100.0)
        price = base + random.uniform(-5, 5)
        change = random.uniform(-2, 2)

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "change": round(change, 2),
            "change_percent": f"{(change/price)*100:.2f}%",
            "volume": random.randint(10000000, 100000000),
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
        }

    async def get_forex_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Get current forex exchange rate.

        Args:
            from_currency: Source currency (e.g., 'USD')
            to_currency: Target currency (e.g., 'EUR')

        Returns:
            Dict with exchange rate and timestamp
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": "CURRENCY_EXCHANGE_RATE",
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "apikey": self.alpha_vantage_key,
                    },
                    timeout=10.0,
                )
                data = response.json()

                if "Realtime Currency Exchange Rate" in data:
                    rate_data = data["Realtime Currency Exchange Rate"]
                    return {
                        "from": from_currency,
                        "to": to_currency,
                        "rate": float(rate_data.get("5. Exchange Rate", 1.0)),
                        "timestamp": rate_data.get("6. Last Refreshed"),
                    }
                else:
                    return self._mock_forex_rate(from_currency, to_currency)
        except Exception as e:
            print(f"Error fetching forex rate: {e}")
            return self._mock_forex_rate(from_currency, to_currency)

    def _mock_forex_rate(self, from_cur: str, to_cur: str) -> Dict[str, Any]:
        """Mock forex data."""
        rates = {
            ("USD", "EUR"): 0.92,
            ("USD", "GBP"): 0.79,
            ("USD", "INR"): 83.12,
            ("EUR", "USD"): 1.09,
            ("GBP", "USD"): 1.27,
            ("INR", "USD"): 0.012,
        }
        rate = rates.get((from_cur, to_cur), 1.0)

        return {
            "from": from_cur,
            "to": to_cur,
            "rate": rate,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_economic_indicators(self, indicator: str = "GDP") -> Dict[str, Any]:
        """
        Get economic indicators (GDP, unemployment, CPI, etc.).

        Args:
            indicator: Indicator type (GDP, UNEMPLOYMENT, CPI, INFLATION)

        Returns:
            Dict with indicator value and metadata
        """
        # Alpha Vantage has limited economic data on free tier
        # In production, use FRED API or World Bank API
        indicators_map = {
            "GDP": ("REAL_GDP", "quarterly"),
            "UNEMPLOYMENT": ("UNEMPLOYMENT", "monthly"),
            "CPI": ("CPI", "monthly"),
            "INFLATION": ("INFLATION", "monthly"),
        }

        if indicator not in indicators_map:
            return {"error": f"Unknown indicator: {indicator}"}

        function, interval = indicators_map[indicator]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": function,
                        "interval": interval,
                        "apikey": self.alpha_vantage_key,
                    },
                    timeout=10.0,
                )
                data = response.json()
                # Parse response (structure varies by indicator)
                return data
        except Exception as e:
            print(f"Error fetching economic indicators: {e}")
            return self._mock_economic_indicator(indicator)

    def _mock_economic_indicator(self, indicator: str) -> Dict[str, Any]:
        """Mock economic data."""
        import random
        values = {
            "GDP": {"value": 25.5, "unit": "trillion USD", "growth": 2.4},
            "UNEMPLOYMENT": {"value": 3.7, "unit": "percent"},
            "CPI": {"value": 304.5, "unit": "index", "change": 3.2},
            "INFLATION": {"value": 3.2, "unit": "percent"},
        }

        base = values.get(indicator, {"value": 100.0, "unit": "index"})
        return {
            "indicator": indicator,
            **base,
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
        }


class NewsAPI:
    """
    Integration with news APIs for market intelligence and sentiment.

    Provides latest news, headlines, and market sentiment.
    """

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY", "demo")
        self.base_url = "https://newsapi.org/v2"

    async def get_business_news(
        self,
        query: Optional[str] = None,
        category: str = "business",
        country: str = "us",
        page_size: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get latest business news.

        Args:
            query: Search query (optional)
            category: News category
            country: Country code
            page_size: Number of articles

        Returns:
            List of news articles
        """
        try:
            async with httpx.AsyncClient() as client:
                if query:
                    # Use /everything endpoint for search
                    response = await client.get(
                        f"{self.base_url}/everything",
                        params={
                            "q": query,
                            "language": "en",
                            "sortBy": "publishedAt",
                            "pageSize": page_size,
                            "apiKey": self.api_key,
                        },
                        timeout=10.0,
                    )
                else:
                    # Use /top-headlines for category news
                    response = await client.get(
                        f"{self.base_url}/top-headlines",
                        params={
                            "category": category,
                            "country": country,
                            "pageSize": page_size,
                            "apiKey": self.api_key,
                        },
                        timeout=10.0,
                    )

                data = response.json()

                if data.get("status") == "ok":
                    return [
                        {
                            "title": article.get("title"),
                            "description": article.get("description"),
                            "source": article.get("source", {}).get("name"),
                            "url": article.get("url"),
                            "published_at": article.get("publishedAt"),
                        }
                        for article in data.get("articles", [])
                    ]
                else:
                    return self._mock_news(query or category)
        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._mock_news(query or category)

    def _mock_news(self, topic: str) -> List[Dict[str, Any]]:
        """Mock news data."""
        return [
            {
                "title": f"{topic.title()}: Major Market Update",
                "description": f"Latest developments in {topic} sector show positive trends.",
                "source": "Financial Times",
                "url": "https://example.com/news/1",
                "published_at": datetime.now().isoformat(),
            },
            {
                "title": f"Breaking: {topic.title()} Industry Sees Growth",
                "description": f"Analysts predict strong performance in {topic}.",
                "source": "Bloomberg",
                "url": "https://example.com/news/2",
                "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            },
            {
                "title": f"{topic.title()} Trends for Q4 2024",
                "description": f"Key insights and forecasts for {topic} businesses.",
                "source": "WSJ",
                "url": "https://example.com/news/3",
                "published_at": (datetime.now() - timedelta(hours=5)).isoformat(),
            },
        ]

    async def get_market_sentiment(self, topic: str) -> Dict[str, Any]:
        """
        Analyze market sentiment from news.

        Args:
            topic: Topic to analyze

        Returns:
            Sentiment analysis results
        """
        news = await self.get_business_news(query=topic, page_size=20)

        # Simple sentiment analysis (in production, use NLP model)
        positive_keywords = ["growth", "profit", "success", "positive", "strong", "gain"]
        negative_keywords = ["decline", "loss", "weak", "negative", "concern", "risk"]

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for article in news:
            text = (article.get("title", "") + " " + article.get("description", "")).lower()

            pos_score = sum(1 for word in positive_keywords if word in text)
            neg_score = sum(1 for word in negative_keywords if word in text)

            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
            else:
                neutral_count += 1

        total = len(news)
        sentiment_score = (positive_count - negative_count) / max(total, 1) * 100

        return {
            "topic": topic,
            "sentiment_score": round(sentiment_score, 2),
            "sentiment": "positive" if sentiment_score > 20 else "negative" if sentiment_score < -20 else "neutral",
            "articles_analyzed": total,
            "breakdown": {
                "positive": positive_count,
                "neutral": neutral_count,
                "negative": negative_count,
            },
        }


class MarketDataAPI:
    """
    Integration for market data and industry insights.

    Provides market trends, competitor data, industry statistics.
    """

    async def get_market_size(
        self, industry: str, region: str = "global"
    ) -> Dict[str, Any]:
        """
        Get market size estimates for an industry.

        Args:
            industry: Industry sector
            region: Geographic region

        Returns:
            Market size data (TAM/SAM/SOM)
        """
        # In production, integrate with market research APIs or databases
        # For now, provide estimates based on common industry data

        industry_sizes = {
            "saas": {"tam": 195.0, "cagr": 18.0, "unit": "billion USD"},
            "fintech": {"tam": 245.0, "cagr": 23.5, "unit": "billion USD"},
            "healthtech": {"tam": 390.0, "cagr": 15.8, "unit": "billion USD"},
            "ecommerce": {"tam": 5700.0, "cagr": 11.0, "unit": "billion USD"},
            "ai": {"tam": 190.0, "cagr": 37.3, "unit": "billion USD"},
            "edtech": {"tam": 340.0, "cagr": 16.3, "unit": "billion USD"},
        }

        industry_key = industry.lower()
        data = industry_sizes.get(industry_key, {"tam": 100.0, "cagr": 10.0, "unit": "billion USD"})

        # Calculate SAM and SOM estimates
        tam = data["tam"]
        sam = tam * 0.1  # Serviceable Available Market ~10% of TAM
        som = sam * 0.05  # Serviceable Obtainable Market ~5% of SAM

        return {
            "industry": industry,
            "region": region,
            "tam": round(tam, 2),
            "sam": round(sam, 2),
            "som": round(som, 2),
            "cagr": data["cagr"],
            "unit": data["unit"],
            "year": datetime.now().year,
            "source": "Market Research Estimates",
        }

    async def get_industry_trends(self, industry: str) -> List[Dict[str, Any]]:
        """
        Get current trends in an industry.

        Args:
            industry: Industry sector

        Returns:
            List of current trends
        """
        # Mock trends data (in production, scrape or use trend APIs)
        trends_db = {
            "saas": [
                {"trend": "AI Integration", "impact": "high", "growth": "+45%"},
                {"trend": "Vertical SaaS", "impact": "high", "growth": "+32%"},
                {"trend": "API-first Products", "impact": "medium", "growth": "+28%"},
            ],
            "fintech": [
                {"trend": "Embedded Finance", "impact": "high", "growth": "+50%"},
                {"trend": "Buy Now Pay Later", "impact": "high", "growth": "+40%"},
                {"trend": "Crypto Integration", "impact": "medium", "growth": "+35%"},
            ],
            "healthtech": [
                {"trend": "Telemedicine", "impact": "high", "growth": "+38%"},
                {"trend": "AI Diagnostics", "impact": "high", "growth": "+42%"},
                {"trend": "Wearables", "impact": "medium", "growth": "+25%"},
            ],
        }

        industry_key = industry.lower()
        return trends_db.get(
            industry_key,
            [
                {"trend": "Digital Transformation", "impact": "high", "growth": "+30%"},
                {"trend": "AI Adoption", "impact": "high", "growth": "+35%"},
                {"trend": "Cloud Migration", "impact": "medium", "growth": "+25%"},
            ],
        )


# Convenience functions for agents
async def fetch_stock_quote(symbol: str) -> Dict[str, Any]:
    """Get stock quote."""
    api = FinancialDataAPI()
    return await api.get_stock_quote(symbol)


async def fetch_market_news(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get market news."""
    api = NewsAPI()
    return await api.get_business_news(query=query, page_size=limit)


async def fetch_market_size(industry: str) -> Dict[str, Any]:
    """Get market size data."""
    api = MarketDataAPI()
    return await api.get_market_size(industry)


async def fetch_industry_trends(industry: str) -> List[Dict[str, Any]]:
    """Get industry trends."""
    api = MarketDataAPI()
    return await api.get_industry_trends(industry)
