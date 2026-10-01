# models/capture.py
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class CaptureModel(BaseModel):

    __tablename__ = "captures"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    packet_count = Column(Integer)
    duration = Column(Float)
    summary = Column(JSON)

    user = relationship("UserModel", back_populates="captures")
    annotations = relationship(
        "AnnotationModel", back_populates="capture", cascade="all, delete-orphan"
    )
    tags = relationship(
        "TagModel", secondary="capture_tags", back_populates="captures"
    )