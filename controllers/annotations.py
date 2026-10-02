# controllers/annotations.py — CRUD for notes on a capture.

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.capture import CaptureModel
from models.annotation import AnnotationModel
from serializers.annotation import AnnotationSchema, AnnotationCreateSchema, AnnotationUpdateSchema
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()


def _owned_capture(capture_id, current_user, db):
    capture = db.query(CaptureModel).filter(
        CaptureModel.id == capture_id,
        CaptureModel.user_id == current_user.id,
    ).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")
    return capture


@router.post("/captures/{capture_id}/annotations", response_model=AnnotationSchema, status_code=201)
def create_annotation(capture_id: int, annotation: AnnotationCreateSchema,
                      db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _owned_capture(capture_id, current_user, db)
    new_annotation = AnnotationModel(
        body=annotation.body, capture_id=capture_id, user_id=current_user.id
    )
    db.add(new_annotation)
    db.commit()
    db.refresh(new_annotation)
    return new_annotation


@router.get("/captures/{capture_id}/annotations", response_model=List[AnnotationSchema])
def list_annotations(capture_id: int, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    _owned_capture(capture_id, current_user, db)
    return db.query(AnnotationModel).filter(AnnotationModel.capture_id == capture_id).all()


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
    db.delete(annotation)
    db.commit()
    return None