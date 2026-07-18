from typing import Optional
import math
from typing import List, Dict, Any
from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.models.copilot import KnowledgeDocument, Embedding
from sqlalchemy import select

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a*b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a*a for a in v1))
    norm2 = math.sqrt(sum(b*b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class RAGService(BaseService):
    def __init__(self, uow: UnitOfWork, event_dispatcher: Optional[EventDispatcher] = None):
        super().__init__(uow, event_dispatcher)

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Simple token/character chunker for Knowledge Base."""
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    def _mock_embed(self, text: str) -> List[float]:
        """Mock embedding generator for demonstration."""
        # Returns a normalized deterministic 10-dimensional vector based on string hash
        h = hash(text)
        vec = [(h >> i) & 1 for i in range(10)]
        norm = math.sqrt(sum(v*v for v in vec))
        if norm == 0:
            return [0.0] * 10
        return [v/norm for v in vec]

    @track_metrics("index_document")
    async def index_document(self, title: str, content: str, source_url: str = None) -> KnowledgeDocument:
        """Chunks, embeds and indexes a document."""
        async def _operation():
            # 1. Create Document
            doc = KnowledgeDocument(
                title=title,
                content=content,
                source_url=source_url
            )
            self.uow.session.add(doc)
            await self.uow.session.flush()

            # 2. Chunking
            chunks = self._chunk_text(content)

            # 3. Embedding
            for idx, chunk_text in enumerate(chunks):
                vector = self._mock_embed(chunk_text)
                emb = Embedding(
                    document_id=doc.id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    vector_data=vector
                )
                self.uow.session.add(emb)

            return doc

        return await self.execute_in_transaction(_operation)

    @track_metrics("vector_search")
    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Finds most relevant document chunks for a given query."""
        async def _operation():
            query_vector = self._mock_embed(query)

            # In production, this would use pgvector's <-> operator.
            # Since vector_data is JSONB, we perform a brute-force cosine similarity in Python for this demo.
            stmt = select(Embedding, KnowledgeDocument).join(KnowledgeDocument)
            res = await self.uow.session.execute(stmt)
            rows = res.all()

            results = []
            for emb, doc in rows:
                sim = cosine_similarity(query_vector, emb.vector_data)
                results.append({
                    "score": sim,
                    "chunk_text": emb.chunk_text,
                    "document_title": doc.title,
                    "document_id": doc.id,
                    "embedding_id": emb.id
                })

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]

        return await self.execute_in_transaction(_operation)
