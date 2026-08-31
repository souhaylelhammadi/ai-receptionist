import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True
