# seed.py — drops and recreates all tables, then seeds initial data.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.environment import DATABASE_URL
from models.base import Base

# Import every model so its table is registered before create_all runs
from models.user import UserModel
from models.capture import CaptureModel
from models.annotation import AnnotationModel
from models.tag import TagModel
from models.capture_tag import CaptureTagModel

from data.user_data import user_list
from data.tag_data import create_test_tags
from data.capture_data import create_test_captures

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Users first, so they get ids
db.add_all(user_list)
db.commit()

# Tags and captures belong to the first user
first_user = user_list[0]
tags = create_test_tags(first_user)
captures = create_test_captures(first_user)
db.add_all(tags + captures)
db.commit()

# Attach one tag to the first capture (seeds the capture_tags join table)
captures[0].tags = [tags[0]]
db.commit()

db.close()
