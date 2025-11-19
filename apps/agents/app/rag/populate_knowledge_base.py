"""
Automated Knowledge Base Population Script.

This script ingests documents from authoritative sources into the RAG system.
Run this to populate the vector database with tax laws, policies, and business guidance.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.rag.ingestion import DocumentIngestionPipeline
from app.rag.knowledge_sources import (
    get_all_sources,
    get_high_priority_sources,
    get_sources_by_category,
)
from app.config import settings
import httpx
from typing import List
from app.rag.knowledge_sources import DocumentSource


async def download_pdf(url: str, output_path: Path) -> bool:
    """Download PDF from URL."""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"✓ Downloaded: {output_path.name}")
            return True
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return False


async def scrape_html(url: str) -> str:
    """Scrape HTML content from URL."""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"✗ Failed to scrape {url}: {e}")
        return ""


async def ingest_source(
    source: DocumentSource, pipeline: DocumentIngestionPipeline, company_id: str
) -> bool:
    """Ingest a single source into the knowledge base."""
    try:
        print(f"\n📄 Processing: {source.title}")
        print(f"   URL: {source.url}")
        print(f"   Category: {source.category} | Jurisdiction: {source.jurisdiction}")

        if source.doc_type == "pdf":
            # Download PDF to temp location
            temp_dir = Path("/tmp/knowledge_base")
            temp_dir.mkdir(exist_ok=True)
            filename = f"{source.jurisdiction}_{source.category}_{source.title[:30].replace(' ', '_')}.pdf"
            temp_path = temp_dir / filename

            if await download_pdf(source.url, temp_path):
                # Ingest PDF
                result = await pipeline.ingest_document(
                    file_path=str(temp_path),
                    company_id=company_id,
                    metadata={
                        "source": source.url,
                        "title": source.title,
                        "category": source.category,
                        "jurisdiction": source.jurisdiction,
                        "priority": source.priority,
                        "doc_type": "government_publication",
                    },
                )
                print(f"   ✓ Ingested {result['chunks_created']} chunks")
                temp_path.unlink()  # Clean up
                return True

        elif source.doc_type == "html":
            # Scrape and ingest HTML
            content = await scrape_html(source.url)
            if content:
                # Parse HTML and extract text
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(content, "html.parser")

                # Remove script and style elements
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()

                # Extract text
                text = soup.get_text(separator="\n", strip=True)

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                text = "\n".join(line for line in lines if line)

                print(f"   ✓ Extracted text ({len(text)} chars from HTML)")

                # Chunk and ingest
                chunks = _chunk_text(text, chunk_size=1000, overlap=100)
                print(f"   ✓ Created {len(chunks)} chunks from HTML")

                # Store each chunk in vector DB
                from app.rag.ingestion import DocumentIngestionPipeline

                pipeline_instance = DocumentIngestionPipeline()
                for i, chunk in enumerate(chunks):
                    await pipeline_instance._store_chunk(
                        chunk_text=chunk,
                        company_id=company_id,
                        metadata={
                            "source": source.url,
                            "title": source.title,
                            "category": source.category,
                            "jurisdiction": source.jurisdiction,
                            "priority": source.priority,
                            "doc_type": "html",
                            "chunk_index": i,
                        },
                    )

                print(f"   ✓ Ingested {len(chunks)} chunks to vector DB")
                return True

        return False


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """
    Chunk text into overlapping segments.

    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk (in characters)
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If not at the end, try to break at a sentence or paragraph
        if end < len(text):
            # Look for paragraph break
            next_para = text.find("\n\n", end)
            next_sentence = text.find(". ", end)

            if next_para != -1 and next_para < end + 200:
                end = next_para
            elif next_sentence != -1 and next_sentence < end + 200:
                end = next_sentence + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward, accounting for overlap
        start = end - overlap if end < len(text) else end

    return chunks

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


async def populate_knowledge_base(
    mode: str = "high_priority", company_id: str = "system"
):
    """
    Populate the knowledge base with documents.

    Args:
        mode: "all", "high_priority", "tax", "legal", "business"
        company_id: Company ID (use "system" for global knowledge)
    """
    print("="* 60)
    print("RAG KNOWLEDGE BASE POPULATION")
    print("=" * 60)
    print(f"Mode: {mode}")
    print(f"Company ID: {company_id}")
    print()

    # Get sources based on mode
    if mode == "all":
        sources = get_all_sources()
    elif mode == "high_priority":
        sources = get_high_priority_sources()
    else:
        sources = get_sources_by_category(mode)

    print(f"📚 Found {len(sources)} sources to ingest\n")

    # Initialize pipeline
    pipeline = DocumentIngestionPipeline()

    # Process each source
    successful = 0
    failed = 0

    for i, source in enumerate(sources, 1):
        print(f"\n[{i}/{len(sources)}]", end=" ")
        if await ingest_source(source, pipeline, company_id):
            successful += 1
        else:
            failed += 1

        # Rate limiting
        await asyncio.sleep(2)  # Be respectful to servers

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total sources: {len(sources)}")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print(f"Success rate: {(successful/len(sources)*100):.1f}%")
    print()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Populate RAG knowledge base with authoritative sources"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "high_priority", "tax", "legal", "business"],
        default="high_priority",
        help="Which sources to ingest",
    )
    parser.add_argument(
        "--company-id",
        default="system",
        help="Company ID for document ownership (default: system for global knowledge)",
    )

    args = parser.parse_args()

    await populate_knowledge_base(mode=args.mode, company_id=args.company_id)


if __name__ == "__main__":
    asyncio.run(main())
