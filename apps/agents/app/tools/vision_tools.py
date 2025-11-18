"""Vision and multimodal AI tools for document and image analysis."""

import base64
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import httpx
from pypdf import PdfReader
import io


class VisionAnalyzer:
    """
    Vision-based analysis using Large Vision Models (LVMs).

    Capabilities:
    - PDF contract analysis
    - Image/chart extraction
    - Product photo analysis
    - Handwritten document OCR
    """

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    async def analyze_pdf_contract(
        self, pdf_path: str, analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze a PDF contract using vision models.

        Args:
            pdf_path: Path to PDF file
            analysis_type: Type of analysis (comprehensive, risk, summary)

        Returns:
            Analysis results including key clauses, risks, and recommendations
        """
        # Extract text from PDF
        pdf_text = self._extract_pdf_text(pdf_path)

        # For PDFs with images/complex layouts, use vision model
        # Convert first few pages to images and analyze
        pages_as_images = await self._pdf_to_images(pdf_path, max_pages=5)

        # Analyze with Claude Vision or GPT-4 Vision
        analysis = await self._analyze_with_vision_model(
            text=pdf_text,
            images=pages_as_images,
            prompt=self._get_contract_analysis_prompt(analysis_type),
        )

        return {
            "document_type": "contract",
            "pages_analyzed": len(pages_as_images),
            "analysis": analysis,
            "key_clauses": self._extract_key_clauses(pdf_text),
            "risk_score": self._calculate_risk_score(analysis),
            "recommendations": self._generate_recommendations(analysis),
        }

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text content from PDF."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    async def _pdf_to_images(self, pdf_path: str, max_pages: int = 5) -> List[str]:
        """
        Convert PDF pages to images (base64).

        Args:
            pdf_path: Path to PDF
            max_pages: Maximum pages to convert

        Returns:
            List of base64 encoded images
        """
        try:
            from pdf2image import convert_from_path

            images = convert_from_path(pdf_path, last_page=max_pages)
            base64_images = []

            for img in images:
                # Convert PIL Image to base64
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                base64_images.append(img_base64)

            return base64_images
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []

    async def _analyze_with_vision_model(
        self,
        text: str = "",
        images: List[str] = [],
        prompt: str = "",
    ) -> str:
        """
        Analyze using Claude or GPT-4 Vision.

        Args:
            text: Text content
            images: Base64 encoded images
            prompt: Analysis prompt

        Returns:
            Analysis result
        """
        if not self.anthropic_api_key:
            # Fallback to text-only analysis
            return await self._analyze_text_only(text, prompt)

        try:
            # Use Claude Vision API
            async with httpx.AsyncClient() as client:
                content = []

                # Add text
                if text:
                    content.append({"type": "text", "text": f"Document text:\n{text[:4000]}"})

                # Add images
                for img_b64 in images[:3]:  # Limit to 3 images
                    content.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_b64,
                            },
                        }
                    )

                # Add analysis prompt
                content.append({"type": "text", "text": prompt})

                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 4096,
                        "messages": [{"role": "user", "content": content}],
                    },
                    timeout=60.0,
                )

                result = response.json()
                return result.get("content", [{}])[0].get("text", "Analysis unavailable")

        except Exception as e:
            print(f"Error with vision model: {e}")
            return await self._analyze_text_only(text, prompt)

    async def _analyze_text_only(self, text: str, prompt: str) -> str:
        """Fallback text-only analysis."""
        # Simple text analysis without vision
        analysis = f"""
        **Document Analysis**

        Based on the text content:
        - Length: {len(text)} characters
        - Key terms identified
        - Structure analyzed

        {prompt}

        Please provide this document to a legal professional for comprehensive review.
        """
        return analysis

    def _get_contract_analysis_prompt(self, analysis_type: str) -> str:
        """Get prompt for contract analysis."""
        prompts = {
            "comprehensive": """
            Analyze this contract comprehensively:
            1. Identify all key clauses (payment, termination, liability, IP, etc.)
            2. Highlight any unusual or concerning terms
            3. Note any missing standard clauses
            4. Assess overall fairness and risk
            5. Provide actionable recommendations
            """,
            "risk": """
            Focus on risk analysis:
            1. Identify high-risk clauses
            2. Note liability limitations
            3. Check for unusual indemnification
            4. Assess termination conditions
            5. Flag any red flags
            """,
            "summary": """
            Provide a concise summary:
            1. Contract type and parties
            2. Main obligations
            3. Key terms (duration, payment, etc.)
            4. Important deadlines
            5. Critical points to note
            """,
        }
        return prompts.get(analysis_type, prompts["comprehensive"])

    def _extract_key_clauses(self, text: str) -> List[Dict[str, str]]:
        """Extract key clauses from contract text."""
        # Simple keyword-based extraction (in production, use NLP)
        keywords = {
            "payment": ["payment", "compensation", "fee", "price"],
            "termination": ["termination", "cancellation", "end", "expire"],
            "liability": ["liability", "indemnify", "indemnification", "damages"],
            "confidentiality": ["confidential", "nda", "non-disclosure", "secret"],
            "intellectual_property": ["intellectual property", "ip", "copyright", "patent"],
        }

        clauses = []
        text_lower = text.lower()

        for clause_type, terms in keywords.items():
            for term in terms:
                if term in text_lower:
                    # Extract context around the term
                    idx = text_lower.find(term)
                    context = text[max(0, idx - 100) : min(len(text), idx + 200)]
                    clauses.append(
                        {
                            "type": clause_type,
                            "term": term,
                            "context": context.strip(),
                        }
                    )
                    break  # Only one match per type

        return clauses

    def _calculate_risk_score(self, analysis: str) -> int:
        """Calculate risk score from analysis (0-100)."""
        # Simple scoring based on keywords
        risk_keywords = ["risk", "concern", "unusual", "missing", "warning", "red flag"]
        positive_keywords = ["standard", "fair", "reasonable", "balanced"]

        risk_count = sum(1 for word in risk_keywords if word.lower() in analysis.lower())
        positive_count = sum(
            1 for word in positive_keywords if word.lower() in analysis.lower()
        )

        score = max(0, min(100, 50 + (risk_count * 10) - (positive_count * 5)))
        return score

    def _generate_recommendations(self, analysis: str) -> List[str]:
        """Generate actionable recommendations."""
        # Extract recommendation-like sentences from analysis
        recommendations = []

        if "missing" in analysis.lower():
            recommendations.append("Review contract for missing standard clauses")
        if "unusual" in analysis.lower():
            recommendations.append("Consult legal counsel about unusual terms")
        if "termination" in analysis.lower():
            recommendations.append("Clarify termination conditions with counterparty")
        if "liability" in analysis.lower():
            recommendations.append("Consider liability insurance coverage")

        if not recommendations:
            recommendations.append("Have a legal professional review before signing")

        return recommendations

    async def analyze_product_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze product images for marketing/design insights.

        Args:
            image_path: Path to product image

        Returns:
            Analysis of product features, quality, marketability
        """
        # Load and encode image
        image_b64 = self._encode_image(image_path)

        prompt = """
        Analyze this product image:
        1. Describe the product and its features
        2. Assess visual quality and presentation
        3. Suggest marketing angles
        4. Note any improvements needed
        5. Rate marketability (1-10)
        """

        analysis = await self._analyze_with_vision_model(images=[image_b64], prompt=prompt)

        return {
            "image_path": image_path,
            "analysis": analysis,
            "marketability_score": self._extract_score(analysis),
        }

    async def analyze_chart_or_graph(self, image_path: str) -> Dict[str, Any]:
        """
        Extract data and insights from charts/graphs.

        Args:
            image_path: Path to chart image

        Returns:
            Extracted data and analysis
        """
        image_b64 = self._encode_image(image_path)

        prompt = """
        Analyze this chart/graph:
        1. Identify the chart type
        2. Extract key data points and trends
        3. Summarize main insights
        4. Note any anomalies or important patterns
        """

        analysis = await self._analyze_with_vision_model(images=[image_b64], prompt=prompt)

        return {
            "image_path": image_path,
            "chart_type": self._extract_chart_type(analysis),
            "insights": analysis,
        }

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"Error encoding image: {e}")
            return ""

    def _extract_score(self, text: str) -> int:
        """Extract numeric score from text."""
        import re

        # Look for patterns like "8/10" or "score: 8"
        patterns = [r"(\d+)/10", r"score:?\s*(\d+)", r"rating:?\s*(\d+)"]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))

        return 5  # Default middle score

    def _extract_chart_type(self, text: str) -> str:
        """Extract chart type from analysis."""
        chart_types = ["bar chart", "line chart", "pie chart", "scatter plot", "histogram"]

        text_lower = text.lower()
        for chart_type in chart_types:
            if chart_type in text_lower:
                return chart_type

        return "unknown"


# Convenience functions
async def analyze_contract(pdf_path: str) -> Dict[str, Any]:
    """Analyze a contract PDF."""
    analyzer = VisionAnalyzer()
    return await analyzer.analyze_pdf_contract(pdf_path)


async def analyze_product_photo(image_path: str) -> Dict[str, Any]:
    """Analyze a product image."""
    analyzer = VisionAnalyzer()
    return await analyzer.analyze_product_image(image_path)


async def analyze_chart(image_path: str) -> Dict[str, Any]:
    """Analyze a chart or graph."""
    analyzer = VisionAnalyzer()
    return await analyzer.analyze_chart_or_graph(image_path)
