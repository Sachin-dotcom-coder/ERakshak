from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/junctions",
    tags=["Junctions"]
)

@router.get("/", response_model=list[schemas.JunctionResponse])
def get_all(db: Session = Depends(get_db)):
    return crud.get_all_junctions(db)

@router.get("/{junction_id}", response_model=schemas.JunctionResponse)
def get_one(junction_id: str, db: Session = Depends(get_db)):

    junction = crud.get_junction(db, junction_id)

    if not junction:
        raise HTTPException(status_code=404, detail="Junction not found")

    return junction

@router.post("/", response_model=schemas.JunctionResponse)
def create(junction: schemas.JunctionCreate,
           db: Session = Depends(get_db)):

    return crud.create_junction(db, junction)

@router.put("/{junction_id}",
            response_model=schemas.JunctionResponse)
def update(junction_id: str,
           junction: schemas.JunctionCreate,
           db: Session = Depends(get_db)):

    updated = crud.update_junction(db, junction_id, junction)

    if not updated:
        raise HTTPException(status_code=404)

    return updated

@router.delete("/{junction_id}")
def delete(junction_id: str,
           db: Session = Depends(get_db)):

    deleted = crud.delete_junction(db, junction_id)

    if not deleted:
        raise HTTPException(status_code=404)

    return {"message": "Deleted successfully"}

