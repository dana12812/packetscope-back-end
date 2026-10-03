# serializers/tag.py — request/response schemas for tags.

from typing import Optional
from pydantic import BaseModel, ConfigDict


class TagCreateSchema(BaseModel):
    name: str
    color: Optional[str] = None

class TagUpdateSchema(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class TagSchema(BaseModel):
    id: int
    name: str
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
        