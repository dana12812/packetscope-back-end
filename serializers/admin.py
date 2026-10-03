# serializers/admin.py — response schemas for the admin pages.

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from serializers.capture import CaptureSchema


class AdminUserSchema(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    capture_count: int
    note_count: int
    last_active: Optional[datetime] = None


class AdminUserDetailSchema(AdminUserSchema):
    captures: List[CaptureSchema] = []


class RoleUpdateSchema(BaseModel):
    role: str


class ActivitySchema(BaseModel):
    id: int
    actor_id: Optional[int] = None
    actor_username: str
    action: str
    target: Optional[str] = None
    capture_id: Optional[int] = None
    capture_exists: bool = False  # lets the UI link only to captures that weren't deleted
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
