# create_admin.py — creates an admin account, or promotes an existing user and resets
# their password. The password is typed at a hidden prompt, so it never lands in code,
# shell history or the repo.
#
#   pipenv run python create_admin.py <username> [--email you@example.com]

import argparse
import getpass
import sys

from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from models import UserModel
from lib.activity import log_activity

MIN_LENGTH = 8

parser = argparse.ArgumentParser(description="Create or promote a PacketScope admin.")
parser.add_argument("username")
parser.add_argument("--email", help="required when creating a new account")
args = parser.parse_args()

password = getpass.getpass("New password: ")
if len(password) < MIN_LENGTH:
    sys.exit(f"Password must be at least {MIN_LENGTH} characters.")
if getpass.getpass("Confirm password: ") != password:
    sys.exit("Passwords don't match.")

db = SessionLocal()
try:
    user = db.query(UserModel).filter(UserModel.username == args.username).first()
    if user:
        user.role = "admin"
        user.set_password(password)
    else:
        if not args.email:
            sys.exit("New account: pass --email too.")
        if db.query(UserModel).filter(UserModel.email == args.email).first():
            sys.exit(f"Email {args.email} is already used by another account.")
        user = UserModel(username=args.username, email=args.email, role="admin")
        user.set_password(password)
        db.add(user)
        db.flush()
        log_activity(db, user, "user.registered")
    db.commit()
finally:
    db.close()
