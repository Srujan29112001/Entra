"""MCP server for legal and compliance tools."""

from ..protocol import MCPServer, MCPTool, MCPToolParameter
from app.tools.vision_tools import VisionAnalyzer


async def analyze_contract_mcp(
    document_url: str,
    document_type: str = "contract",
    jurisdiction: str = "US",
) -> dict:
    """MCP wrapper for contract analysis."""
    analyzer = VisionAnalyzer()
    result = await analyzer.analyze_contract(
        document_url=document_url,
        contract_type=document_type,
    )
    return result


async def extract_clauses_mcp(document_url: str, clause_types: list = None) -> dict:
    """MCP wrapper for clause extraction."""
    analyzer = VisionAnalyzer()
    # Basic extraction - would expand with specific clause detection
    analysis = await analyzer.analyze_contract(document_url=document_url)
    return {
        "clauses": analysis.get("key_terms", []),
        "risks": analysis.get("risks", []),
        "recommendations": analysis.get("recommendations", []),
    }


def create_legal_server() -> MCPServer:
    """Create and configure the Legal & Compliance MCP server."""
    server = MCPServer(
        name="legal",
        description="Legal document analysis, contract review, and compliance",
    )

    # Contract analysis
    server.register_tool(
        MCPTool(
            name="analyze_contract",
            description="Analyze legal contracts using vision AI",
            parameters=[
                MCPToolParameter(
                    name="document_url",
                    type="string",
                    description="URL or path to contract document",
                    required=True,
                ),
                MCPToolParameter(
                    name="document_type",
                    type="string",
                    description="Type of contract",
                    required=False,
                    default="contract",
                    enum=["contract", "nda", "term_sheet", "employment", "license"],
                ),
                MCPToolParameter(
                    name="jurisdiction",
                    type="string",
                    description="Legal jurisdiction",
                    required=False,
                    default="US",
                    enum=["US", "UK", "IN", "EU"],
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "key_terms": {"type": "array"},
                    "risks": {"type": "array"},
                    "recommendations": {"type": "array"},
                },
            },
            category="legal",
        ),
        analyze_contract_mcp,
    )

    # Clause extraction
    server.register_tool(
        MCPTool(
            name="extract_clauses",
            description="Extract specific clauses from legal documents",
            parameters=[
                MCPToolParameter(
                    name="document_url",
                    type="string",
                    description="URL or path to document",
                    required=True,
                ),
                MCPToolParameter(
                    name="clause_types",
                    type="array",
                    description="Types of clauses to extract",
                    required=False,
                ),
            ],
            returns={
                "type": "object",
                "properties": {
                    "clauses": {"type": "array"},
                    "risks": {"type": "array"},
                    "recommendations": {"type": "array"},
                },
            },
            category="legal",
        ),
        extract_clauses_mcp,
    )

    return server
