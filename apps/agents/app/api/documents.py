"""Document upload and processing API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.ingestion import pipeline

router = APIRouter()


class IngestRequest(BaseModel):
    """Document ingestion request."""

    file_url: str
    company_id: str
    document_type: str


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
    try:
        # TODO: Download file from URL
        # For now, assume file is accessible

        result = await pipeline.ingest_file(
            file_path=request.file_url,  # In production, download first
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


@router.get("/list/{company_id}")
async def list_documents(company_id: str):
    """List all documents for a company."""
    # TODO: Query database for documents
    return {"documents": []}
