# serializers/capture.py — request/response schemas for captures.

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from serializers.tag import TagSchema


class CaptureUpdateSchema(BaseModel):
    filename: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class CaptureSchema(BaseModel):
    id: int
    filename: str
    packet_count: Optional[int] = None
    duration: Optional[float] = None
    summary: Optional[dict] = None
    user_id: int
    created_at: datetime
    tags: List[TagSchema] = []

    class Config:
        orm_mode = True