"""Document upload and processing API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.ingestion import pipeline
from app.config import settings
from supabase.client import create_client
import httpx
import tempfile
import os
from pathlib import Path

router = APIRouter()


class IngestRequest(BaseModel):
    """Document ingestion request."""

    file_url: str
    company_id: str
    document_type: str


async def download_file_from_url(url: str, destination: str) -> str:
    """
    Download a file from a URL to a local destination.

    Args:
        url: URL of the file to download
        destination: Local path to save the file

    Returns:
        Path to the downloaded file
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Save to destination
            with open(destination, "wb") as f:
                f.write(response.content)

            return destination

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download file: {str(e)}")


@router.post("/ingest")
async def ingest_document(request: IngestRequest):
    """
    Ingest a document into the RAG system.

    This endpoint:
    1. Downloads the document from the URL
    2. Processes it (extracts text, chunks it)
    3. Creates embeddings
    4. Stores in vector database
    """
    temp_file = None
    try:
        # Download file from URL to temporary location
        if request.file_url.startswith("http"):
            # Create temporary file with appropriate extension
            file_ext = Path(request.file_url).suffix or ".pdf"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            temp_file.close()

            file_path = await download_file_from_url(request.file_url, temp_file.name)
        else:
            # Assume it's a local file path
            file_path = request.file_url

        # Ingest the file
        result = await pipeline.ingest_file(
            file_path=file_path,
            company_id=request.company_id,
            document_type=request.document_type,
        )

        return {
            "success": True,
            "message": "Document ingested successfully",
            "chunks_created": result["chunks_created"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


@router.get("/list/{company_id}")
async def list_documents(company_id: str):
    """
    List all documents for a company.

    Args:
        company_id: Company identifier

    Returns:
        List of documents with metadata
    """
    try:
        # Connect to Supabase
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        # Query documents table
        result = supabase.table("documents") \
            .select("id, title, document_type, file_path, created_at, metadata") \
            .eq("company_id", company_id) \
            .order("created_at", desc=True) \
            .execute()

        documents = result.data if result.data else []

        return {
            "success": True,
            "company_id": company_id,
            "count": len(documents),
            "documents": documents
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")
