# models/__init__.py — import all models so SQLAlchemy can resolve relationships between them.

from .base import Base
from .user import UserModel
from .capture import CaptureModel
from .annotation import AnnotationModel
from .tag import TagModel
from .capture_tag import CaptureTagModel
from .activity import ActivityModel
