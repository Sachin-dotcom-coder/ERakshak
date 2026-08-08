from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/intrusions",
    tags=["BRTS Intrusions"]
)


# -----------------------------
# Get all intrusions
# -----------------------------
@router.get("/", response_model=list[schemas.IntrusionResponse])
def get_all_intrusions(db: Session = Depends(get_db)):
    return crud.get_all_intrusions(db)


# -----------------------------
# Get intrusions by junction
# -----------------------------
@router.get("/{junction_id}", response_model=list[schemas.IntrusionResponse])
def get_intrusions_by_junction(
    junction_id: str,
    db: Session = Depends(get_db)
):
    return crud.get_intrusions_by_junction(db, junction_id)


# -----------------------------
# Create intrusion
# -----------------------------
@router.post("/", response_model=schemas.IntrusionResponse)
def create_intrusion(
    intrusion: schemas.IntrusionCreate,
    db: Session = Depends(get_db)
):
    return crud.create_intrusion(db, intrusion)


# -----------------------------
# Delete intrusion
# -----------------------------
@router.delete("/{intrusion_id}")
def delete_intrusion(
    intrusion_id: int,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_intrusion(db, intrusion_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Intrusion not found"
        )

    return {
        "message": "Intrusion deleted successfully"
    }

@router.put("/{intrusion_id}", response_model=schemas.IntrusionResponse)
def update_intrusion(
    intrusion_id: int,
    intrusion: schemas.IntrusionCreate,
    db: Session = Depends(get_db)
):
    updated = crud.update_intrusion(
        db,
        intrusion_id,
        intrusion
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Intrusion not found"
        )

    return updated