# models/activity.py
# Activity log: one row per thing a user did. The actor's username is copied onto the
# row so the history stays readable after an admin deletes that user.

from sqlalchemy import Column, Integer, String
from .base import BaseModel


class ActivityModel(BaseModel):

    __tablename__ = "activities"

    actor_id = Column(Integer, index=True)  # no FK on purpose: rows outlive deleted users
    actor_username = Column(String, nullable=False)
    action = Column(String, nullable=False)  # e.g. "capture.uploaded"
    target = Column(String)  # human-readable subject, e.g. a filename
    capture_id = Column(Integer)
