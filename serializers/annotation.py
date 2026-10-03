# serializers/annotation.py — request/response schemas for annotations (notes).

from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AnnotationCreateSchema(BaseModel):
    body: str

class AnnotationUpdateSchema(BaseModel):
    body: str


class AnnotationSchema(BaseModel):
    id: int
    body: str
    capture_id: int
    user_id: int
    author_username: Optional[str] = None
    author_role: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
        