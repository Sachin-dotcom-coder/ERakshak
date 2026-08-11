from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas

from database import get_db

router = APIRouter(
    prefix="/events",
    tags=["Lane Events"]
)

@router.get("/")
def get_all(
    db: Session = Depends(get_db)
):

    return crud.get_all_lane_events(db)

@router.get("/{junction_id}")
def get_junction(
    junction_id: str,
    db: Session = Depends(get_db)
):

    return crud.get_lane_events_by_junction(
        db,
        junction_id
    )

@router.post("/")
def create(
    event: schemas.LaneEventCreate,
    db: Session = Depends(get_db)
):

    return crud.create_lane_event(
        db,
        event
    )

@router.put("/{event_id}")
def update(
    event_id: int,
    event: schemas.LaneEventCreate,
    db: Session = Depends(get_db)
):

    updated = crud.update_lane_event(
        db,
        event_id,
        event
    )

    if not updated:
        raise HTTPException(404)

    return updated

@router.delete("/{event_id}")
def delete(
    event_id: int,
    db: Session = Depends(get_db)
):

    deleted = crud.delete_lane_event(
        db,
        event_id
    )

    if not deleted:
        raise HTTPException(404)

    return {
        "message": "Deleted"
    }

