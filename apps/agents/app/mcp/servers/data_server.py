"""MCP server for data and external API tools."""

from ..protocol import MCPServer, MCPTool, MCPToolParameter
from app.tools.external_apis import ExternalAPIs


async def get_stock_data_mcp(symbol: str, period: str = "1mo") -> dict:
    """MCP wrapper for stock data."""
    api = ExternalAPIs()
    return await api.get_stock_quote(symbol, period=period)


async def get_economic_data_mcp(indicator: str, country: str = "US") -> dict:
    """MCP wrapper for economic indicators."""
    api = ExternalAPIs()
    return await api.get_economic_indicator(indicator, country=country)


async def get_market_news_mcp(
    query: str, category: str = "business", limit: int = 10
) -> dict:
    """MCP wrapper for market news."""
    api = ExternalAPIs()
    return await api.get_news(query, category=category, page_size=limit)


async def get_forex_rate_mcp(from_currency: str, to_currency: str) -> dict:
    """MCP wrapper for forex rates."""
    api = ExternalAPIs()
    return await api.get_forex_rate(from_currency, to_currency)


def create_data_server() -> MCPServer:
    """Create and configure the Data & External APIs MCP server."""
    server = MCPServer(
        name="data",
        description="External data sources, market data, news, and economic indicators",
    )

    # Stock data
    server.register_tool(
        MCPTool(
            name="get_stock_data",
            description="Get real-time stock market data",
            parameters=[
                MCPToolParameter(
                    name="symbol",
                    type="string",
                    description="Stock ticker symbol",
                    required=True,
                ),
                MCPToolParameter(
                    name="period",
                    type="string",
                    description="Time period for data",
                    required=False,
                    default="1mo",
                    enum=["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"],
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "price": {"type": "number"},
                    "change": {"type": "number"},
                    "volume": {"type": "number"},
                },
            },
            category="data",
        ),
        get_stock_data_mcp,
    )

    # Economic indicators
    server.register_tool(
        MCPTool(
            name="get_economic_data",
            description="Get economic indicators (GDP, inflation, unemployment, etc.)",
            parameters=[
                MCPToolParameter(
                    name="indicator",
                    type="string",
                    description="Economic indicator type",
                    required=True,
                    enum=["gdp", "inflation", "unemployment", "interest_rate", "cpi"],
                ),
                MCPToolParameter(
                    name="country",
                    type="string",
                    description="Country code",
                    required=False,
                    default="US",
                    enum=["US", "UK", "IN", "CN", "EU"],
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "indicator": {"type": "string"},
                    "value": {"type": "number"},
                    "date": {"type": "string"},
                    "trend": {"type": "string"},
                },
            },
            category="data",
        ),
        get_economic_data_mcp,
    )

    # Market news
    server.register_tool(
        MCPTool(
            name="get_market_news",
            description="Get latest market and business news",
            parameters=[
                MCPToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                ),
                MCPToolParameter(
                    name="category",
                    type="string",
                    description="News category",
                    required=False,
                    default="business",
                    enum=["business", "technology", "markets", "startups"],
                ),
                MCPToolParameter(
                    name="limit",
                    type="number",
                    description="Number of articles to return",
                    required=False,
                    default=10,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "articles": {"type": "array"},
                    "total": {"type": "number"},
                },
            },
            category="data",
        ),
        get_market_news_mcp,
    )

    # Forex rates
    server.register_tool(
        MCPTool(
            name="get_forex_rate",
            description="Get foreign exchange rates",
            parameters=[
                MCPToolParameter(
                    name="from_currency",
                    type="string",
                    description="Source currency code",
                    required=True,
                ),
                MCPToolParameter(
                    name="to_currency",
                    type="string",
                    description="Target currency code",
                    required=True,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "rate": {"type": "number"},
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
            },
            category="data",
        ),
        get_forex_rate_mcp,
    )

    return server
