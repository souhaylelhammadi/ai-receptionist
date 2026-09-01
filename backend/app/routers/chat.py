from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document_chunk import DocumentChunk
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.deps import get_current_user
from app.services.embeddings import generate_embedding
from app.services.chat_agent import generate_chat_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query_embedding = generate_embedding(payload.message)

    results = (
        db.query(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .filter(DocumentChunk.company_id == current_user.company_id)
        .order_by("distance")
        .limit(3)
        .all()
    )

    context_chunks = [chunk.content for chunk, _ in results]
    used_titles = list({chunk.document.title for chunk, _ in results})

    reply = generate_chat_response(payload.message, context_chunks)

    return ChatResponse(reply=reply, used_documents=used_titles)
