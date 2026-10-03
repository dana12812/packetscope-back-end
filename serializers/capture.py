# serializers/capture.py — request/response schemas for captures.

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
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
    owner_username: Optional[str] = None
    created_at: datetime
    tags: List[TagSchema] = []

    model_config = ConfigDict(from_attributes=True)
