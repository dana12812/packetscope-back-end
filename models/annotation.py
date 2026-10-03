# models/annotation.py

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class AnnotationModel(BaseModel):

    __tablename__ = "annotations"

    capture_id = Column(Integer, ForeignKey("captures.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)

    capture = relationship("CaptureModel", back_populates="annotations")
    user = relationship("UserModel", back_populates="annotations")

    # Shown above each note so readers know who wrote it
    @property
    def author_username(self):
        return self.user.username if self.user else None

    @property
    def author_role(self):
        return self.user.role if self.user else None