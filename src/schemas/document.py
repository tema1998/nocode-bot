from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentIn(BaseModel):
    rubrics: list[str]
    text: str


class DocumentOut(DocumentIn):
    id: UUID
    created_at: datetime
