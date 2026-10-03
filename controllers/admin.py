# controllers/admin.py — admin-only routes: manage users and read the activity log.

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.user import UserModel
from models.capture import CaptureModel
from models.annotation import AnnotationModel
from models.tag import TagModel
from models.activity import ActivityModel
from serializers.admin import AdminUserSchema, AdminUserDetailSchema, RoleUpdateSchema, ActivitySchema
from database import get_db
from dependencies.require_admin import require_admin
from lib.activity import log_activity

router = APIRouter(prefix="/admin")

ROLES = {"user", "admin"}


def _user_or_404(user_id, db):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _summaries(users, db):
    """Adds capture/note counts and last activity time to each user."""
    ids = [u.id for u in users]
    capture_counts = dict(db.query(CaptureModel.user_id, func.count(CaptureModel.id))
                          .filter(CaptureModel.user_id.in_(ids)).group_by(CaptureModel.user_id).all())
    note_counts = dict(db.query(AnnotationModel.user_id, func.count(AnnotationModel.id))
                       .filter(AnnotationModel.user_id.in_(ids)).group_by(AnnotationModel.user_id).all())
    last_active = dict(db.query(ActivityModel.actor_id, func.max(ActivityModel.created_at))
                       .filter(ActivityModel.actor_id.in_(ids)).group_by(ActivityModel.actor_id).all())
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at,
            "capture_count": capture_counts.get(u.id, 0),
            "note_count": note_counts.get(u.id, 0),
            "last_active": last_active.get(u.id),
        }
        for u in users
    ]


@router.get("/users", response_model=List[AdminUserSchema])
def list_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    users = db.query(UserModel).order_by(UserModel.created_at).all()
    return _summaries(users, db)


@router.get("/users/{user_id}", response_model=AdminUserDetailSchema)
def get_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = _user_or_404(user_id, db)
    summary = _summaries([user], db)[0]
    captures = (db.query(CaptureModel).filter(CaptureModel.user_id == user.id)
                .order_by(CaptureModel.created_at.desc()).all())
    return {**summary, "captures": captures}


@router.patch("/users/{user_id}", response_model=AdminUserSchema)
def update_role(user_id: int, update: RoleUpdateSchema,
                db: Session = Depends(get_db), admin=Depends(require_admin)):
    if update.role not in ROLES:
        raise HTTPException(status_code=422, detail="Role must be 'user' or 'admin'")
    user = _user_or_404(user_id, db)
    if user.id == admin.id and update.role != "admin":
        raise HTTPException(status_code=400, detail="You can't remove your own admin role")

    user.role = update.role
    log_activity(db, admin, "user.role_changed", f"{user.username} → {update.role}")
    db.commit()
    db.refresh(user)
    return _summaries([user], db)[0]


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = _user_or_404(user_id, db)
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You can't delete your own account")

    # Remove everything the user owns. Deleting through the ORM also clears the
    # capture_tags rows, and each capture's notes cascade with it.
    db.query(AnnotationModel).filter(AnnotationModel.user_id == user.id).delete(synchronize_session=False)
    for capture in db.query(CaptureModel).filter(CaptureModel.user_id == user.id).all():
        db.delete(capture)
    for tag in db.query(TagModel).filter(TagModel.user_id == user.id).all():
        db.delete(tag)

    log_activity(db, admin, "user.deleted", user.username)
    db.delete(user)
    db.commit()
    return None


@router.get("/activity", response_model=List[ActivitySchema])
def list_activity(user_id: Optional[int] = None, limit: int = 100,
                  db: Session = Depends(get_db), admin=Depends(require_admin)):
    query = db.query(ActivityModel)
    if user_id is not None:
        query = query.filter(ActivityModel.actor_id == user_id)
    rows = query.order_by(ActivityModel.created_at.desc(), ActivityModel.id.desc()).limit(min(limit, 500)).all()

    capture_ids = {r.capture_id for r in rows if r.capture_id}
    existing = {cid for (cid,) in db.query(CaptureModel.id).filter(CaptureModel.id.in_(capture_ids)).all()}
    return [
        {
            "id": r.id,
            "actor_id": r.actor_id,
            "actor_username": r.actor_username,
            "action": r.action,
            "target": r.target,
            "capture_id": r.capture_id,
            "capture_exists": r.capture_id in existing,
            "created_at": r.created_at,
        }
        for r in rows
    ]
