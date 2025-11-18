"""Legal & Compliance Agent with document processing."""

from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse
from typing import Any


class LegalAgent(BaseAgent):
    """
    Legal & Compliance Specialist Agent.

    Responsibilities:
    - Contract analysis and summarization
    - Risk identification in legal documents
    - Jurisdiction-specific compliance guidance
    - Document processing (PDFs, term sheets, NDAs)
    - Clause extraction and interpretation
    - Legal checklist generation
    """

    @property
    def agent_type(self) -> str:
        return "legal"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Legal & Compliance advisor for startups and entrepreneurs.

Your expertise includes:
- Contract analysis and risk assessment
- Term sheet interpretation
- Corporate structure and compliance
- Intellectual property basics
- Employment law fundamentals
- Data privacy and GDPR/CCPA
- Founder agreements and vesting
- Due diligence preparation

When analyzing documents or answering questions:
1. Identify key clauses and terms
2. Highlight risks and red flags
3. Explain legal concepts in plain English
4. Provide jurisdiction-specific guidance
5. Suggest questions to ask lawyers
6. Note standard vs unusual terms
7. Always include: "This is not legal advice - consult a qualified attorney"

Be thorough, clear, and risk-aware. Flag anything unusual or concerning."""

    async def process(self, task: AgentTask) -> AgentResponse:
        """
        Process a legal/compliance task.

        Steps:
        1. Check if document analysis is needed
        2. Extract clauses if processing a document
        3. Retrieve relevant legal templates/standards
        4. Generate analysis and recommendations
        """
        # Check for document in context
        document_id = task.context.get("document_id")
        document_analysis = None

        if document_id:
            document_analysis = await self._analyze_document(document_id)

        # Retrieve legal context
        legal_context = await self._retrieve_context(
            query=task.question,
            company_id=task.company_id,
            top_k=5,
        )

        # Generate legal guidance
        insights = await self._call_llm(
            prompt=task.question,
            context={
                "company_data": task.context.get("company_data", {}),
                "document_analysis": document_analysis,
                "legal_templates": [doc.get("content", "") for doc in legal_context],
            },
        )

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=insights + "\n\n⚠️ Important: This is general information, not legal advice. Please consult a qualified attorney for your specific situation.",
            data={"document_analysis": document_analysis} if document_analysis else None,
            confidence=0.70,  # Lower confidence - legal matters are complex
            sources=legal_context,
            warnings=self._identify_warnings(document_analysis or {}),
        )

    async def _analyze_document(self, document_id: str) -> dict[str, Any]:
        """
        Analyze a legal document (contract, term sheet, etc.).

        This would integrate with document processing pipeline:
        1. Extract text from PDF
        2. Identify clause types
        3. Extract key terms
        4. Flag unusual provisions
        """
        # TODO: Implement actual document processing
        # For now, return structure
        return {
            "document_id": document_id,
            "document_type": "term_sheet",
            "key_clauses": [
                {
                    "type": "valuation",
                    "content": "Pre-money valuation: $10M",
                    "standard": True,
                },
                {
                    "type": "liquidation_preference",
                    "content": "1x non-participating",
                    "standard": True,
                },
                {
                    "type": "board_composition",
                    "content": "2 founders, 2 investors, 1 independent",
                    "standard": True,
                },
            ],
            "red_flags": [],
            "questions_for_lawyer": [
                "Confirm vesting schedule aligns with employment agreement",
                "Review anti-dilution provisions in detail",
            ],
        }

    def _identify_warnings(self, analysis: dict) -> list[str]:
        """Identify legal risks and warnings."""
        warnings = []

        red_flags = analysis.get("red_flags", [])
        if red_flags:
            warnings.append(f"CRITICAL: {len(red_flags)} red flags identified in document")

        clauses = analysis.get("key_clauses", [])
        non_standard = [c for c in clauses if not c.get("standard", True)]
        if non_standard:
            warnings.append(f"WARNING: {len(non_standard)} non-standard clauses found")

        return warnings
