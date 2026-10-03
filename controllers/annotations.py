# controllers/annotations.py — CRUD for notes on a capture.
# Owners and admins can read and add notes; only a note's author can edit or delete it.

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.capture import CaptureModel
from models.annotation import AnnotationModel
from serializers.annotation import AnnotationSchema, AnnotationCreateSchema, AnnotationUpdateSchema
from database import get_db
from dependencies.get_current_user import get_current_user
from lib.activity import log_activity

router = APIRouter()


def _readable_capture(capture_id, current_user, db):
    query = db.query(CaptureModel).filter(CaptureModel.id == capture_id)
    if not current_user.is_admin:
        query = query.filter(CaptureModel.user_id == current_user.id)
    capture = query.first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")
    return capture


@router.post("/captures/{capture_id}/annotations", response_model=AnnotationSchema, status_code=201)
def create_annotation(capture_id: int, annotation: AnnotationCreateSchema,
                      db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    capture = _readable_capture(capture_id, current_user, db)
    new_annotation = AnnotationModel(
        body=annotation.body, capture_id=capture_id, user_id=current_user.id
    )
    db.add(new_annotation)
    log_activity(db, current_user, "note.added", capture.filename, capture.id)
    db.commit()
    db.refresh(new_annotation)
    return new_annotation


@router.get("/captures/{capture_id}/annotations", response_model=List[AnnotationSchema])
def list_annotations(capture_id: int, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    _readable_capture(capture_id, current_user, db)
    return (db.query(AnnotationModel).filter(AnnotationModel.capture_id == capture_id)
            .order_by(AnnotationModel.created_at).all())


@router.put("/annotations/{annotation_id}", response_model=AnnotationSchema)
def update_annotation(annotation_id: int, updates: AnnotationUpdateSchema,
                      db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    annotation = db.query(AnnotationModel).filter(
        AnnotationModel.id == annotation_id,
        AnnotationModel.user_id == current_user.id,
    ).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    annotation.body = updates.body
    log_activity(db, current_user, "note.edited", annotation.capture.filename, annotation.capture_id)
    db.commit()
    db.refresh(annotation)
    return annotation


@router.delete("/annotations/{annotation_id}", status_code=204)
def delete_annotation(annotation_id: int, db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    annotation = db.query(AnnotationModel).filter(
        AnnotationModel.id == annotation_id,
        AnnotationModel.user_id == current_user.id,
    ).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    log_activity(db, current_user, "note.deleted", annotation.capture.filename, annotation.capture_id)
    db.delete(annotation)
    db.commit()
    return None