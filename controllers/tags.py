# controllers/tags.py — CRUD for a user's tags.

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.tag import TagModel
from serializers.tag import TagSchema, TagCreateSchema, TagUpdateSchema
from database import get_db
from dependencies.get_current_user import get_current_user
from lib.activity import log_activity

router = APIRouter()


@router.post("/tags", response_model=TagSchema, status_code=201)
def create_tag(tag: TagCreateSchema, db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    new_tag = TagModel(name=tag.name, color=tag.color, user_id=current_user.id)
    db.add(new_tag)
    log_activity(db, current_user, "tag.created", tag.name)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.get("/tags", response_model=List[TagSchema])
def list_tags(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(TagModel).filter(TagModel.user_id == current_user.id).all()


@router.put("/tags/{tag_id}", response_model=TagSchema)
def update_tag(tag_id: int, updates: TagUpdateSchema, db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    tag = db.query(TagModel).filter(
        TagModel.id == tag_id, TagModel.user_id == current_user.id
    ).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if updates.name is not None and updates.name != tag.name:
        log_activity(db, current_user, "tag.renamed", f"{tag.name} → {updates.name}")
        tag.name = updates.name
    if updates.color is not None:
        tag.color = updates.color

    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    tag = db.query(TagModel).filter(
        TagModel.id == tag_id, TagModel.user_id == current_user.id
    ).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    log_activity(db, current_user, "tag.deleted", tag.name)
    db.delete(tag)
    db.commit()
    return None