# controllers/captures.py — CRUD for captures, scoped to the logged-in user.

import os
import tempfile
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from models.capture import CaptureModel
from models.tag import TagModel
from serializers.capture import CaptureSchema, CaptureUpdateSchema
from database import get_db
from dependencies.get_current_user import get_current_user
from lib.pcap_parser import parse_pcap

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/captures", response_model=CaptureSchema, status_code=201)
def create_capture(file: UploadFile = File(...),
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):

    contents = file.file.read()

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413,
                            detail="File is larger than the 5 MB limit")

    # Scapy reads from a path, so write the upload to a temp file, then clean up
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pcap") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        summary = parse_pcap(tmp_path)
    except Exception:
        raise HTTPException(status_code=400,
                            detail="Could not read file as a .pcap capture")
    finally:
        os.remove(tmp_path)

    new_capture = CaptureModel(
        user_id=current_user.id,
        filename=file.filename,
        packet_count=summary["packet_count"],
        duration=summary["duration"],
        summary=summary,
    )
    db.add(new_capture)
    db.commit()
    db.refresh(new_capture)
    return new_capture


@router.get("/captures", response_model=List[CaptureSchema])
def list_captures(db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):

    return db.query(CaptureModel).filter(
        CaptureModel.user_id == current_user.id
    ).all()


@router.get("/captures/{capture_id}", response_model=CaptureSchema)
def get_capture(capture_id: int,
                db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):

    capture = db.query(CaptureModel).filter(
        CaptureModel.id == capture_id,
        CaptureModel.user_id == current_user.id,
    ).first()

    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")

    return capture


@router.put("/captures/{capture_id}", response_model=CaptureSchema)
def update_capture(capture_id: int,
                   updates: CaptureUpdateSchema,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):

    capture = db.query(CaptureModel).filter(
        CaptureModel.id == capture_id,
        CaptureModel.user_id == current_user.id,
    ).first()

    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")

    if updates.filename is not None:
        capture.filename = updates.filename

    if updates.tag_ids is not None:
        capture.tags = db.query(TagModel).filter(
            TagModel.id.in_(updates.tag_ids),
            TagModel.user_id == current_user.id,
        ).all()

    db.commit()
    db.refresh(capture)
    return capture


@router.delete("/captures/{capture_id}", status_code=204)
def delete_capture(capture_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):

    capture = db.query(CaptureModel).filter(
        CaptureModel.id == capture_id,
        CaptureModel.user_id == current_user.id,
    ).first()

    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")

    db.delete(capture)
    db.commit()
    return None