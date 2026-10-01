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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

try:
    print("Recreating database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Seeding the database...")
    db = SessionLocal()
    db.add_all(user_list)
    db.commit()
    db.close()

    print("Database seeding complete!")
except Exception as e:
    print("An error occurred:", e)