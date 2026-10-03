# controllers/users.py — auth routes: register, login, and current user.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import UserModel
from serializers.user import UserSchema, UserRegistrationSchema, UserLoginSchema, UserTokenSchema
from database import get_db
from dependencies.get_current_user import get_current_user
from lib.activity import log_activity
from config.environment import ADMIN_USERNAMES

router = APIRouter()


@router.post("/register", response_model=UserTokenSchema, status_code=201)
def create_user(user: UserRegistrationSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    new_user = UserModel(username=user.username, email=user.email)
    new_user.set_password(user.password)

    db.add(new_user)
    db.flush()  # assigns new_user.id for the activity row
    log_activity(db, new_user, "user.registered")
    db.commit()
    db.refresh(new_user)

    token = new_user.generate_token()

    return {"token": token, "message": "Registration successful"}


@router.post("/login", response_model=UserTokenSchema, status_code=201)
def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()

    if not db_user or not db_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    log_activity(db, db_user, "user.signed_in")
    # Promotion happens at sign-in only (never at sign-up), so register the account
    # first and then list it in ADMIN_USERNAMES — nobody can claim a listed name.
    if db_user.username.lower() in ADMIN_USERNAMES and not db_user.is_admin:
        db_user.role = "admin"
        log_activity(db, db_user, "user.role_changed", f"{db_user.username} → admin (ADMIN_USERNAMES)")
    db.commit()

    token = db_user.generate_token()

    return {"token": token, "message": "Login successful"}


@router.get("/current_user", response_model=UserSchema)
def current_user(user: UserSchema = Depends(get_current_user)):
    return user