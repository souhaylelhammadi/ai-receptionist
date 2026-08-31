import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.database import Base
from app.config import settings


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)

    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    document = relationship("Document", backref="chunks")

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
