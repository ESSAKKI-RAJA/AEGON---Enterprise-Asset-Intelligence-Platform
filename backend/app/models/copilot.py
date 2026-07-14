import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase

class Conversation(AuditableBase):
    """
    Copilot AI Chat session details log.
    """
    __tablename__ = "conversations"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    messages: Mapped[List["ConversationMessage"]] = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
    memory: Mapped[Optional["ConversationMemory"]] = relationship("ConversationMemory", back_populates="conversation", uselist=False, cascade="all, delete-orphan")

class ConversationMessage(AuditableBase):
    """
    Individual chat turns.
    """
    __tablename__ = "conversation_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. USER, ASSISTANT, SYSTEM
    content: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    retrieved_contexts: Mapped[List["RetrievedContext"]] = relationship("RetrievedContext", back_populates="message", cascade="all, delete-orphan")

class PromptTemplate(AuditableBase):
    """
    System templates used to guide copilot behavior.
    """
    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    template_text: Mapped[str] = mapped_column(Text, nullable=False)

class KnowledgeDocument(AuditableBase):
    """
    Main source documents indexed for future RAG queries.
    """
    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    embeddings: Mapped[List["Embedding"]] = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")

class Embedding(AuditableBase):
    """
    Generated vector representations configurations chunks.
    """
    __tablename__ = "embeddings"

    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    vector_data: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False) # Store floats array as JSONB for RAG compatibility

    document: Mapped["KnowledgeDocument"] = relationship("KnowledgeDocument", back_populates="embeddings")
    references: Mapped[List["VectorReference"]] = relationship("VectorReference", back_populates="embedding", cascade="all, delete-orphan")

class VectorReference(AuditableBase):
    """
    Bridges embedding references mapping back to target tables.
    """
    __tablename__ = "vector_references"

    embedding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("embeddings.id", ondelete="CASCADE"), nullable=False, index=True)
    referenced_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    referenced_entity_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. ASSET, WORK_ORDER

    embedding: Mapped["Embedding"] = relationship("Embedding", back_populates="references")

class RetrievedContext(AuditableBase):
    """
    RAG outputs mapped directly back to chat messages.
    """
    __tablename__ = "retrieved_contexts"

    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversation_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    context_text: Mapped[str] = mapped_column(Text, nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)

    message: Mapped["ConversationMessage"] = relationship("ConversationMessage", back_populates="retrieved_contexts")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="retrieved_context", cascade="all, delete-orphan")

class Citation(AuditableBase):
    """
    Citations pointing back to document source context.
    """
    __tablename__ = "citations"

    retrieved_context_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("retrieved_contexts.id", ondelete="CASCADE"), nullable=False, index=True)
    source_document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    retrieved_context: Mapped["RetrievedContext"] = relationship("RetrievedContext", back_populates="citations")

class LLMRequest(AuditableBase):
    """
    Logs of external requests sent to model provider.
    """
    __tablename__ = "llm_requests"

    provider: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. OpenAI, Anthropic, Google
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class LLMResponse(AuditableBase):
    """
    Matching model outputs logs.
    """
    __tablename__ = "llm_responses"

    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("llm_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    response_payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class ConversationMemory(AuditableBase):
    """
    Summarized conversational memory logs to keep context active.
    """
    __tablename__ = "conversation_memories"

    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="memory")
