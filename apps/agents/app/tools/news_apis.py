"""
Real-Time News API Integration.

Provides access to business news, market news, and policy updates from real sources.
"""

import httpx
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class NewsAPIClient:
    """
    NewsAPI client for real-time business and market news.

    API Docs: https://newsapi.org/docs
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize NewsAPI client."""
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "NEWS_API_KEY not set. Get one at https://newsapi.org/register"
            )
        self.base_url = "https://newsapi.org/v2"

    async def get_top_headlines(
        self,
        category: str = "business",
        country: str = "us",
        q: Optional[str] = None,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        Get top headlines.

        Args:
            category: Category (business, technology, etc.)
            country: Country code (us, gb, in, etc.)
            q: Search query
            page_size: Number of articles

        Returns:
            Dictionary with articles
        """
        async with httpx.AsyncClient() as client:
            params = {
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": page_size,
            }

            if q:
                params["q"] = q

            response = await client.get(
                f"{self.base_url}/top-headlines",
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def search_everything(
        self,
        q: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        sort_by: str = "publishedAt",  # publishedAt, relevancy, popularity
        language: str = "en",
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search all articles.

        Args:
            q: Search query
            from_date: Start date
            to_date: End date
            sort_by: Sort order
            language: Language code
            page_size: Number of articles

        Returns:
            Dictionary with articles
        """
        async with httpx.AsyncClient() as client:
            params = {
                "apiKey": self.api_key,
                "q": q,
                "sortBy": sort_by,
                "language": language,
                "pageSize": page_size,
            }

            if from_date:
                params["from"] = from_date.strftime("%Y-%m-%d")
            else:
                # Default to last 7 days
                params["from"] = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            if to_date:
                params["to"] = to_date.strftime("%Y-%m-%d")

            response = await client.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_market_news(
        self,
        industry: Optional[str] = None,
        days_back: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get market and business news relevant to entrepreneurs."""
        query_parts = ["startup OR entrepreneur OR business OR market"]

        if industry:
            query_parts.append(f'AND "{industry}"')

        query = " ".join(query_parts)

        result = await self.search_everything(
            q=query,
            from_date=datetime.now() - timedelta(days=days_back),
            sort_by="publishedAt",
            page_size=10,
        )

        articles = result.get("articles", [])

        # Format articles
        formatted_articles = []
        for article in articles:
            formatted_articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
            })

        return formatted_articles

    async def get_policy_news(
        self,
        country: str = "us",
        days_back: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get policy, tax, and regulatory news."""
        query = "policy OR regulation OR tax OR law OR government AND business"

        result = await self.search_everything(
            q=query,
            from_date=datetime.now() - timedelta(days=days_back),
            sort_by="publishedAt",
            page_size=10,
        )

        articles = result.get("articles", [])

        # Format and filter articles
        formatted_articles = []
        for article in articles:
            formatted_articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "type": "policy",
            })

        return formatted_articles


class NewsAggregator:
    """
    Aggregates news from multiple sources for entrepreneur insights.
    """

    def __init__(self, news_api_key: Optional[str] = None):
        """Initialize news aggregator."""
        self.news_api = NewsAPIClient(news_api_key) if news_api_key else None

    async def get_entrepreneur_briefing(
        self,
        industry: Optional[str] = None,
        country: str = "us",
    ) -> Dict[str, Any]:
        """
        Get a daily briefing for entrepreneurs.

        Returns:
            Dictionary with categorized news
        """
        if not self.news_api:
            return {
                "market_news": [],
                "policy_news": [],
                "industry_news": [],
                "summary": "News API not configured. Set NEWS_API_KEY.",
            }

        # Fetch different categories in parallel
        market_news = await self.news_api.get_market_news(industry=industry)
        policy_news = await self.news_api.get_policy_news(country=country)

        # Get industry-specific news if specified
        industry_news = []
        if industry:
            industry_result = await self.news_api.search_everything(
                q=f'"{industry}" AND (funding OR startup OR innovation)',
                page_size=5,
            )
            industry_news = [
                {
                    "title": a.get("title", ""),
                    "description": a.get("description", ""),
                    "url": a.get("url", ""),
                    "published_at": a.get("publishedAt", ""),
                    "source": a.get("source", {}).get("name", "Unknown"),
                }
                for a in industry_result.get("articles", [])
            ]

        # Generate summary
        total_articles = len(market_news) + len(policy_news) + len(industry_news)

        summary = (
            f"Briefing for {datetime.now().strftime('%Y-%m-%d')}: "
            f"{total_articles} relevant articles found. "
        )

        if market_news:
            summary += f"{len(market_news)} market updates. "
        if policy_news:
            summary += f"{len(policy_news)} policy/regulatory changes. "
        if industry_news:
            summary += f"{len(industry_news)} industry-specific news. "

        return {
            "market_news": market_news[:5],
            "policy_news": policy_news[:5],
            "industry_news": industry_news[:5],
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
        }

    async def search_company_news(
        self,
        company_name: str,
        days_back: int = 30,
    ) -> List[Dict[str, Any]]:
        """Search for news about a specific company."""
        if not self.news_api:
            return []

        result = await self.news_api.search_everything(
            q=f'"{company_name}"',
            from_date=datetime.now() - timedelta(days=days_back),
            page_size=10,
        )

        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
            }
            for a in result.get("articles", [])
        ]


# Export for easy imports
__all__ = [
    "NewsAPIClient",
    "NewsAggregator",
]
