from sqlalchemy.orm import Session

import models
import schemas

def create_junction(db: Session, junction: schemas.JunctionCreate):

    db_junction = models.Junction(**junction.model_dump())

    db.add(db_junction)

    db.commit()

    db.refresh(db_junction)

    return db_junction

def get_all_junctions(db: Session):

    return db.query(models.Junction).all()

def get_junction(db: Session, junction_id: str):

    return (
        db.query(models.Junction)
        .filter(models.Junction.junction_id == junction_id)
        .first()
    )

def update_junction(
    db: Session,
    junction_id: str,
    junction: schemas.JunctionCreate,
):

    db_junction = (
        db.query(models.Junction)
        .filter(models.Junction.junction_id == junction_id)
        .first()
    )

    if not db_junction:
        return None

    for key, value in junction.model_dump().items():
        setattr(db_junction, key, value)

    db.commit()

    db.refresh(db_junction)

    return db_junction

def delete_junction(db: Session, junction_id: str):

    db_junction = (
        db.query(models.Junction)
        .filter(models.Junction.junction_id == junction_id)
        .first()
    )

    if not db_junction:
        return None

    db.delete(db_junction)

    db.commit()

    return db_junction

def create_lane(db: Session, lane: schemas.LaneCreate):

    db_lane = models.Lane(**lane.model_dump())

    db.add(db_lane)

    db.commit()

    db.refresh(db_lane)

    return db_lane

def get_all_lanes(db: Session):

    return db.query(models.Lane).all()

def get_lane(db: Session, lane_id: str):

    return (
        db.query(models.Lane)
        .filter(models.Lane.lane_id == lane_id)
        .first()
    )

def update_lane(
    db: Session,
    lane_id: str,
    lane: schemas.LaneCreate,
):

    db_lane = (
        db.query(models.Lane)
        .filter(models.Lane.lane_id == lane_id)
        .first()
    )

    if not db_lane:
        return None

    for key, value in lane.model_dump().items():
        setattr(db_lane, key, value)

    db.commit()

    db.refresh(db_lane)

    return db_lane

def delete_lane(db: Session, lane_id: str):

    db_lane = (
        db.query(models.Lane)
        .filter(models.Lane.lane_id == lane_id)
        .first()
    )

    if not db_lane:
        return None

    db.delete(db_lane)

    db.commit()

    return db_lane

def create_lane_event(
    db: Session,
    event: schemas.LaneEventCreate,
):

    db_event = models.LaneEvent(**event.model_dump())

    db.add(db_event)

    db.commit()

    db.refresh(db_event)

    return db_event

def get_all_lane_events(db: Session):

    return db.query(models.LaneEvent).all()

def get_lane_events_by_junction(
    db: Session,
    junction_id: str,
):

    return (
        db.query(models.LaneEvent)
        .filter(models.LaneEvent.junction_id == junction_id)
        .order_by(models.LaneEvent.recorded_at.desc())
        .all()
    )

def update_lane_event(
    db: Session,
    event_id: int,
    event: schemas.LaneEventCreate,
):

    db_event = (
        db.query(models.LaneEvent)
        .filter(models.LaneEvent.id == event_id)
        .first()
    )

    if not db_event:
        return None

    for key, value in event.model_dump().items():
        setattr(db_event, key, value)

    db.commit()

    db.refresh(db_event)

    return db_event

def delete_lane_event(
    db: Session,
    event_id: int,
):

    db_event = (
        db.query(models.LaneEvent)
        .filter(models.LaneEvent.id == event_id)
        .first()
    )

    if not db_event:
        return None

    db.delete(db_event)

    db.commit()

    return db_event

def create_intrusion(
    db: Session,
    intrusion: schemas.IntrusionCreate,
):

    db_intrusion = models.BRTSIntrusion(
        **intrusion.model_dump()
    )

    db.add(db_intrusion)

    db.commit()

    db.refresh(db_intrusion)

    return db_intrusion

def get_all_intrusions(db: Session):

    return db.query(models.BRTSIntrusion).all()

def get_intrusions_by_junction(
    db: Session,
    junction_id: str,
):

    return (
        db.query(models.BRTSIntrusion)
        .filter(
            models.BRTSIntrusion.junction_id == junction_id
        )
        .all()
    )

def delete_intrusion(
    db: Session,
    intrusion_id: int,
):

    intrusion = (
        db.query(models.BRTSIntrusion)
        .filter(models.BRTSIntrusion.id == intrusion_id)
        .first()
    )

    if not intrusion:
        return None

    db.delete(intrusion)

    db.commit()

    return intrusion

def create_signal(
    db: Session,
    signal: schemas.SignalCreate,
):

    db_signal = models.SignalStatus(
        **signal.model_dump()
    )

    db.add(db_signal)

    db.commit()

    db.refresh(db_signal)

    return db_signal

def get_signal(
    db: Session,
    junction_id: str,
):

    return (
        db.query(models.SignalStatus)
        .filter(
            models.SignalStatus.junction_id == junction_id
        )
        .first()
    )

def update_signal(
    db: Session,
    junction_id: str,
    signal: schemas.SignalCreate,
):

    db_signal = (
        db.query(models.SignalStatus)
        .filter(
            models.SignalStatus.junction_id == junction_id
        )
        .first()
    )

    if not db_signal:
        return None

    for key, value in signal.model_dump().items():
        setattr(db_signal, key, value)

    db.commit()

    db.refresh(db_signal)

    return db_signal

def update_intrusion(
    db: Session,
    intrusion_id: int,
    intrusion: schemas.IntrusionCreate,
):
    db_intrusion = (
        db.query(models.BRTSIntrusion)
        .filter(models.BRTSIntrusion.id == intrusion_id)
        .first()
    )

    if not db_intrusion:
        return None

    for key, value in intrusion.model_dump().items():
        setattr(db_intrusion, key, value)

    db.commit()
    db.refresh(db_intrusion)

    return db_intrusion