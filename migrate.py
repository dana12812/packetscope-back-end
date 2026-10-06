# migrate.py — upgrades an existing database for roles and the activity log
# without dropping data (seed.py recreates everything from scratch instead).
# Safe to run more than once.

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.environment import DATABASE_URL
from models import Base, UserModel
from data.user_data import create_test_users

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    conn.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR NOT NULL DEFAULT 'user'"
    ))

# Creates the activities table (existing tables are left alone)
Base.metadata.create_all(bind=engine)

# Make sure at least one admin exists so the admin page is reachable
db = sessionmaker(bind=engine)()
if not db.query(UserModel).filter(UserModel.role == "admin").first():
    seed_admin = next(u for u in create_test_users() if u.role == "admin")
    existing = db.query(UserModel).filter(UserModel.username == seed_admin.username).first()
    if existing:
        existing.role = "admin"
    else:
        db.add(seed_admin)
    db.commit()
db.close()
