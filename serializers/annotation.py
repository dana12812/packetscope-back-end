# serializers/annotation.py — request/response schemas for annotations (notes).

from pydantic import BaseModel
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
    created_at: datetime

    class Config:
        orm_mode = True
        