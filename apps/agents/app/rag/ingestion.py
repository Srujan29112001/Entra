"""Document ingestion pipeline."""

from typing import List
from pathlib import Path
import asyncio
from app.rag.retriever import retriever, processor
from app.config import settings


class IngestionPipeline:
    """
    Document ingestion pipeline.

    Orchestrates the end-to-end process:
    1. File upload / URL fetch
    2. Document processing (PDF, text, etc.)
    3. Chunking and embedding
    4. Storage in vector DB
    5. Metadata indexing
    """

    def __init__(self):
        """Initialize the pipeline."""
        self.retriever = retriever
        self.processor = processor

    async def ingest_file(
        self,
        file_path: str,
        company_id: str,
        document_type: str,
        metadata: dict | None = None,
    ) -> dict:
        """
        Ingest a single file.

        Args:
            file_path: Path to file
            company_id: Company identifier
            document_type: Type of document (tax, legal, financial, etc.)
            metadata: Additional metadata

        Returns:
            Ingestion result
        """
        # Determine file type
        path = Path(file_path)
        extension = path.suffix.lower()

        # Process based on type
        if extension == ".pdf":
            chunks = await self.processor.process_pdf(file_path)
        elif extension in [".txt", ".md"]:
            with open(file_path, "r") as f:
                text = f.read()
            chunks = await self.processor.process_text(text)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

        # Add metadata
        for chunk in chunks:
            chunk["metadata"].update({
                "company_id": company_id,
                "document_type": document_type,
                **(metadata or {}),
            })

        # Add to vector store
        doc_ids = await self.retriever.add_documents(chunks)

        return {
            "file_path": file_path,
            "chunks_created": len(chunks),
            "document_ids": doc_ids,
            "company_id": company_id,
            "document_type": document_type,
        }

    async def ingest_batch(
        self,
        file_paths: List[str],
        company_id: str,
        document_type: str,
    ) -> dict:
        """
        Ingest multiple files in parallel.

        Args:
            file_paths: List of file paths
            company_id: Company identifier
            document_type: Document type

        Returns:
            Batch ingestion results
        """
        tasks = [
            self.ingest_file(path, company_id, document_type)
            for path in file_paths
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]

        return {
            "total_files": len(file_paths),
            "successful": len(successful),
            "failed": len(failed),
            "results": successful,
            "errors": [str(e) for e in failed],
        }

    async def ingest_government_data(self, country: str) -> dict:
        """
        Ingest government tax and policy data for a country.

        This would fetch and process:
        - Tax laws and regulations
        - Startup schemes and incentives
        - Compliance requirements
        - Official government resources

        Args:
            country: Country code (US, IN, UK, etc.)

        Returns:
            Ingestion results
        """
        # URLs to government resources (examples)
        urls = {
            "US": [
                "https://www.irs.gov/forms-pubs/about-publication-334",
                # More IRS resources
            ],
            "IN": [
                "https://www.incometax.gov.in/iec/foportal/help/individual",
                # More tax resources
            ],
        }

        country_urls = urls.get(country, [])

        results = []
        for url in country_urls:
            try:
                chunks = await self.processor.process_url(url)

                # Add country-specific metadata
                for chunk in chunks:
                    chunk["metadata"].update({
                        "country": country,
                        "document_type": "tax_law",
                        "source": "government",
                    })

                doc_ids = await self.retriever.add_documents(chunks)

                results.append({
                    "url": url,
                    "chunks": len(chunks),
                    "document_ids": doc_ids,
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "error": str(e),
                })

        return {
            "country": country,
            "sources_processed": len(results),
            "results": results,
        }


# Global pipeline instance
pipeline = IngestionPipeline()
