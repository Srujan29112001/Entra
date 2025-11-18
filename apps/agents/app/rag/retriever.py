"""RAG retriever for vector search."""

from typing import Any, List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import create_client
from app.config import settings


class RAGRetriever:
    """
    Retrieval-Augmented Generation system.

    Uses pgvector in Supabase for semantic search over documents,
    enabling agents to ground their responses in real data.

    Architecture:
    1. Documents are ingested and chunked
    2. Chunks are embedded using OpenAI embeddings
    3. Embeddings stored in Supabase with pgvector
    4. At query time, semantic search retrieves relevant chunks
    5. Chunks are passed to agents as context
    """

    def __init__(self):
        """Initialize the retriever."""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )

        self.supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        self.vector_store = SupabaseVectorStore(
            client=self.supabase,
            embedding=self.embeddings,
            table_name="documents",
            query_name="match_documents",
        )

    async def retrieve(
        self,
        query: str,
        company_id: str | None = None,
        document_type: str | None = None,
        top_k: int = 5,
    ) -> List[dict[str, Any]]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            company_id: Filter by company ID
            document_type: Filter by document type (tax, legal, market, etc.)
            top_k: Number of results to return

        Returns:
            List of relevant document chunks with metadata
        """
        # Build filter
        filter_dict = {}
        if company_id:
            filter_dict["company_id"] = company_id
        if document_type:
            filter_dict["document_type"] = document_type

        # Perform similarity search
        results = await self.vector_store.asimilarity_search_with_relevance_scores(
            query=query,
            k=top_k,
            filter=filter_dict if filter_dict else None,
        )

        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score,
            })

        return formatted_results

    async def add_documents(
        self,
        documents: List[dict[str, Any]],
        company_id: str | None = None,
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of documents with 'content' and 'metadata'
            company_id: Associate documents with a company

        Returns:
            List of document IDs
        """
        from langchain.schema import Document

        # Convert to LangChain documents
        docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            if company_id:
                metadata["company_id"] = company_id

            docs.append(Document(
                page_content=doc["content"],
                metadata=metadata,
            ))

        # Add to vector store
        ids = await self.vector_store.aadd_documents(docs)
        return ids


class DocumentProcessor:
    """
    Process various document types for ingestion.

    Handles:
    - PDFs (tax documents, contracts, term sheets)
    - Text files
    - Web pages
    - Structured data (JSON, CSV)
    """

    def __init__(self):
        """Initialize the document processor."""
        pass

    async def process_pdf(self, file_path: str) -> List[dict[str, Any]]:
        """
        Process a PDF document.

        Args:
            file_path: Path to PDF file

        Returns:
            List of processed chunks
        """
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # Load PDF
        loader = PyPDFLoader(file_path)
        pages = await loader.aload()

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        chunks = text_splitter.split_documents(pages)

        # Format for ingestion
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            formatted_chunks.append({
                "content": chunk.page_content,
                "metadata": {
                    **chunk.metadata,
                    "chunk_id": i,
                    "source": file_path,
                },
            })

        return formatted_chunks

    async def process_text(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> List[dict[str, Any]]:
        """
        Process plain text.

        Args:
            text: Text content
            metadata: Optional metadata

        Returns:
            List of processed chunks
        """
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        chunks = text_splitter.split_text(text)

        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            formatted_chunks.append({
                "content": chunk,
                "metadata": {
                    **(metadata or {}),
                    "chunk_id": i,
                },
            })

        return formatted_chunks

    async def process_url(self, url: str) -> List[dict[str, Any]]:
        """
        Process a web page.

        Args:
            url: URL to process

        Returns:
            List of processed chunks
        """
        from langchain_community.document_loaders import WebBaseLoader

        loader = WebBaseLoader(url)
        documents = await loader.aload()

        return await self.process_text(
            text=documents[0].page_content,
            metadata={"source": url, "type": "web"},
        )


# Global instances
retriever = RAGRetriever()
processor = DocumentProcessor()
