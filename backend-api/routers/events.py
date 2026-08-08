from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/events",
    tags=["Lane Events"]
)

@router.get("/{junction_id}")
def get_junction_data(
    junction_id: str,
    db: Session = Depends(get_db)
):
    return crud.get_lane_events_by_junction(
        db,
        junction_id
    )

@router.get("/")
def get_all_junction_data(
    db: Session = Depends(get_db)
):
    return crud.get_all_lane_events(db)

@router.post("/")
def post_junction_data(
    event: schemas.LaneEventCreate,
    db: Session = Depends(get_db)
):
    return crud.create_lane_event(
        db,
        event
    )

@router.put("/{event_id}")
def update_event(
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
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return updated

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):

    deleted = crud.delete_lane_event(
        db,
        event_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return {
        "message": "Deleted successfully"
    }

