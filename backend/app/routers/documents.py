import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentListItem
from app.core.deps import get_current_user
from app.services.chunking import split_text_into_chunks
from app.services.embeddings import generate_embeddings_batch

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Crée le document (le texte source complet)
    document = Document(
        title=payload.title,
        content=payload.content,
        company_id=current_user.company_id,
    )
    db.add(document)
    db.flush()  # récupère document.id avant le commit final

    # 2. Découpe le contenu en chunks
    chunks_text = split_text_into_chunks(payload.content)

    # 3. Génère les embeddings pour tous les chunks en un seul appel API
    embeddings = generate_embeddings_batch(chunks_text)

    # 4. Sauvegarde chaque chunk avec son embedding
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
    db.delete(document)  # les chunks liés seront orphelins ; on gérera le cascade proprement plus tard
    db.commit()
    return None