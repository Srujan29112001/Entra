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

        This integrates with document processing pipeline:
        1. Extract text from PDF
        2. Identify clause types
        3. Extract key terms
        4. Flag unusual provisions
        """
        try:
            from app.tools.vision_tools import VisionAnalyzer
            from supabase.client import create_client
            from app.config import settings
            import tempfile
            import os

            # Get document from database
            supabase = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key,
            )

            result = supabase.table("documents").select("*").eq("id", document_id).single().execute()

            if not result.data:
                raise ValueError(f"Document {document_id} not found")

            document = result.data
            file_path = document.get("file_path")

            if not file_path:
                raise ValueError("Document has no file path")

            # If it's a Supabase storage path, download it
            if file_path.startswith("documents/"):
                storage_response = supabase.storage.from_("documents").download(file_path)

                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(storage_response)
                    temp_path = tmp_file.name

                file_path = temp_path

            # Analyze with vision tools
            analyzer = VisionAnalyzer()
            analysis = await analyzer.analyze_pdf_contract(file_path, analysis_type="comprehensive")

            # Clean up temp file if created
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)

            return {
                "document_id": document_id,
                "document_type": analysis.get("document_type", "contract"),
                "key_clauses": analysis.get("key_clauses", []),
                "red_flags": self._extract_red_flags(analysis),
                "questions_for_lawyer": analysis.get("recommendations", []),
                "risk_score": analysis.get("risk_score", 0),
            }

        except Exception as e:
            print(f"Error analyzing document: {e}")
            # Return structured fallback
            return {
                "document_id": document_id,
                "document_type": "unknown",
                "key_clauses": [],
                "red_flags": [],
                "questions_for_lawyer": ["Unable to analyze document - please upload again or consult a lawyer"],
                "error": str(e),
            }

    def _extract_red_flags(self, analysis: dict) -> list[str]:
        """Extract red flags from vision analysis."""
        red_flags = []

        # Check analysis text for warning keywords
        analysis_text = str(analysis.get("analysis", "")).lower()

        warning_keywords = [
            "unusual", "non-standard", "concerning", "risk",
            "unfavorable", "aggressive", "problematic"
        ]

        for keyword in warning_keywords:
            if keyword in analysis_text:
                red_flags.append(f"Contains {keyword} terms or clauses")

        return list(set(red_flags))  # Remove duplicates

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
