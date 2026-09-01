import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentListItem,
    SearchQuery,
    SearchResult,
)
from app.core.deps import get_current_user
from app.services.chunking import split_text_into_chunks
from app.services.embeddings import generate_embedding, generate_embeddings_batch

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = Document(
        title=payload.title,
        content=payload.content,
        company_id=current_user.company_id,
    )
    db.add(document)
    db.flush()

    chunks_text = split_text_into_chunks(payload.content)
    embeddings = generate_embeddings_batch(chunks_text)

    for index, (chunk_text, embedding) in enumerate(zip(chunks_text, embeddings)):
        chunk = DocumentChunk(
            content=chunk_text,
            chunk_index=index,
            embedding=embedding,
            document_id=document.id,
            company_id=current_user.company_id,
        )
        db.add(chunk)

    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentListItem])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Document)
        .filter(Document.company_id == current_user.company_id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.company_id == current_user.company_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable.")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.company_id == current_user.company_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable.")
    db.delete(document)
    db.commit()
    return None


@router.post("/search", response_model=list[SearchResult])
def search_documents(
    payload: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query_embedding = generate_embedding(payload.query)

    results = (
        db.query(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .filter(DocumentChunk.company_id == current_user.company_id)
        .order_by("distance")
        .limit(payload.top_k)
        .all()
    )

    return [
        SearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_title=chunk.document.title,
            content=chunk.content,
            similarity_score=1 - distance,
        )
        for chunk, distance in results
    ]
