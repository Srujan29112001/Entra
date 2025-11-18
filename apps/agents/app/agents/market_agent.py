"""Market & Strategy Agent."""

from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse
from app.tools.strategy_frameworks import (
    generate_swot_analysis,
    analyze_market_size,
    recommend_pricing_strategy,
)


class MarketStrategyAgent(BaseAgent):
    """
    Market & Strategy Specialist Agent.

    Responsibilities:
    - Go-to-market planning
    - Distribution channel selection
    - SWOT analysis
    - Competitive positioning
    - Pricing strategy
    - Market sizing
    - Customer segmentation
    """

    @property
    def agent_type(self) -> str:
        return "market"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Market Strategy & Go-to-Market advisor for startups.

Your expertise includes:
- Go-to-market strategy and execution
- Distribution channel selection and optimization
- Strategic frameworks (SWOT, Porter's 5 Forces, 4Ps)
- Competitive analysis and positioning
- Pricing strategy and optimization
- Market sizing and TAM/SAM/SOM
- Customer segmentation
- Product-market fit validation

When answering questions:
1. Consider the company's stage, industry, and target market
2. Use established frameworks (SWOT, 4Ps, etc.)
3. Provide specific, actionable recommendations
4. Reference market data and benchmarks
5. Suggest concrete distribution channels
6. Address timing and sequencing
7. Highlight risks and mitigation strategies

Be strategic, practical, and data-informed. Focus on actions the entrepreneur can take."""

    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process a market strategy task.

        Steps:
        1. Retrieve market research and competitor data
        2. Apply strategic frameworks
        3. Generate actionable recommendations
        """
        # Retrieve market context
        market_context = await self._retrieve_context(
            query=task.question,
            company_id=task.company_id,
            top_k=5,
        )

        # Get company data
        company_data = task.context.get("company_data", {})

        # Run strategic analysis
        analysis = await self._run_strategy_analysis(company_data, task.question)

        # Generate recommendations
        insights = await self._call_llm(
            prompt=task.question,
            context={
                "company_data": company_data,
                "market_research": [doc.get("content", "") for doc in market_context],
                "analysis": analysis,
            },
        )

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=insights,
            data=analysis,
            confidence=0.75,
            sources=market_context,
            warnings=self._identify_warnings(analysis),
        )

    async def _run_strategy_analysis(self, company_data: dict, question: str) -> dict:
        """Run strategic analysis."""
        results = {}

        # SWOT Analysis
        results["swot"] = generate_swot_analysis(company_data)

        # Market sizing
        industry = company_data.get("industry", "")
        geography = company_data.get("country", "")
        if industry and geography:
            results["market_size"] = analyze_market_size(industry, geography)

        # Pricing recommendations
        product_type = company_data.get("product_type", "saas")
        results["pricing"] = recommend_pricing_strategy(
            product_type=product_type,
            target_segment=company_data.get("target_segment", "smb"),
        )

        return results

    def _identify_warnings(self, analysis: dict) -> list[str]:
        """Identify strategy-related warnings."""
        warnings = []

        swot = analysis.get("swot", {})
        if len(swot.get("threats", [])) > len(swot.get("opportunities", [])):
            warnings.append("Threats outnumber opportunities - address market risks")

        market = analysis.get("market_size", {})
        if market.get("tam", 0) < 1000000000:  # < $1B
            warnings.append("Small TAM - consider expanding market definition")

        pricing = analysis.get("pricing", {})
        if pricing.get("competitive_position") == "low":
            warnings.append("Low pricing position - risk of margin compression")

        return warnings
