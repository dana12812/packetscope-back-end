# models/capture_tag.py
# Join table linking captures and tags (many-to-many).

from sqlalchemy import Column, Integer, ForeignKey
from .base import BaseModel


class CaptureTagModel(BaseModel):

    __tablename__ = "capture_tags"

    capture_id = Column(Integer, ForeignKey("captures.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)