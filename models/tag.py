# models/tag.py
# Tag model: a user's color-coded label that can be attached to many captures.

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class TagModel(BaseModel):

    __tablename__ = "tags"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String)

    user = relationship("UserModel", back_populates="tags")
    captures = relationship(
        "CaptureModel", secondary="capture_tags", back_populates="tags"
    )