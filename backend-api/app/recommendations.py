import datetime
from sqlalchemy.orm import Session
from app.models import Recommendation, Violation, TrafficMetric, Lane

def run_recommendation_engine(db: Session, junction_id: str):
    """
    Analyzes recent metrics and violations for a junction,
    and logs engineering recommendations if thresholds are crossed.
    """
    now = datetime.datetime.utcnow()
    ten_minutes_ago = now - datetime.timedelta(minutes=10)

    # Rule 1: High BRTS Intrusion Rate
    # If there are >= 3 intrusions in the last 10 minutes on any BRTS lane of this junction,
    # recommend physical channelization.
    brts_lanes = db.query(Lane).filter(Lane.junction_id == junction_id, Lane.is_brts == True).all()
    for lane in brts_lanes:
        intrusion_count = db.query(Violation).filter(
            Violation.lane_id == lane.id,
            Violation.violation_type == "brts_intrusion",
            Violation.timestamp >= ten_minutes_ago
        ).count()

        if intrusion_count >= 3:
            # Check if we already logged this recommendation in the last hour
            one_hour_ago = now - datetime.timedelta(hours=1)
            existing = db.query(Recommendation).filter(
                Recommendation.junction_id == junction_id,
                Recommendation.issue_type == "brts_intrusion_heavy",
                Recommendation.timestamp >= one_hour_ago
            ).first()

            if not existing:
                rec = Recommendation(
                    junction_id=junction_id,
                    timestamp=now,
                    issue_type="brts_intrusion_heavy",
                    severity="high",
                    description=f"Frequent BRTS lane encroachment ({intrusion_count} events in 10m) on {lane.lane_name}.",
                    suggested_action=f"Install physical concrete channelizers or plastic bollards at the entry points of {lane.lane_name} to deter private vehicles.",
                    status="pending"
                )
                db.add(rec)
                db.commit()
                print(f"Recommendation logged: BRTS Intrusion Heavy at {junction_id}")

    # Rule 2: Asymmetric Traffic Flow (Dynamic Lane Reversal)
    # Compare North-South or East-West queues. If queue in direction A is > 2.5x direction B,
    # and direction A queue is significant (> 50m), suggest dynamic lane reversal.
    direction_queues = {"N": 0.0, "S": 0.0, "E": 0.0, "W": 0.0}
    lanes = db.query(Lane).filter(Lane.junction_id == junction_id).all()
    for lane in lanes:
        # Get the latest metric for this lane
        latest_metric = db.query(TrafficMetric).filter(
            TrafficMetric.lane_id == lane.id
        ).order_by(TrafficMetric.timestamp.desc()).first()
        
        if latest_metric:
            direction_queues[lane.direction] = max(direction_queues[lane.direction], latest_metric.queue_length_m)

    # Check N-S imbalance
    n_q = direction_queues["N"]
    s_q = direction_queues["S"]
    if n_q > 0 and s_q > 0:
        if (n_q > 50 and n_q >= 2.5 * s_q) or (s_q > 50 and s_q >= 2.5 * n_q):
            heavy_dir = "Northbound" if n_q > s_q else "Southbound"
            light_dir = "Southbound" if n_q > s_q else "Northbound"
            
            # Prevent spam: check past hour
            one_hour_ago = now - datetime.timedelta(hours=1)
            existing = db.query(Recommendation).filter(
                Recommendation.junction_id == junction_id,
                Recommendation.issue_type == "asymmetric_flow",
                Recommendation.timestamp >= one_hour_ago
            ).first()

            if not existing:
                rec = Recommendation(
                    junction_id=junction_id,
                    timestamp=now,
                    issue_type="asymmetric_flow",
                    severity="medium",
                    description=f"Severe asymmetric flow detected: {heavy_dir} queue ({max(n_q, s_q):.1f}m) is over 2.5x {light_dir} queue ({min(n_q, s_q):.1f}m).",
                    suggested_action=f"Activate dynamic overhead lane indicators to allocate one lane from {light_dir} to the opposing {heavy_dir} traffic flow.",
                    status="pending"
                )
                db.add(rec)
                db.commit()
                print(f"Recommendation logged: Asymmetric Flow at {junction_id}")

    # Rule 3: Heavy Queue Spillback (Phase Timing / Bottleneck)
    # If average queue length across non-BRTS lanes is > 70m, recommend signal timing recalibration
    non_brts_lanes = [l for l in lanes if not l.is_brts]
    if non_brts_lanes:
        total_q = 0.0
        for lane in non_brts_lanes:
            latest_metric = db.query(TrafficMetric).filter(TrafficMetric.lane_id == lane.id).order_by(TrafficMetric.timestamp.desc()).first()
            if latest_metric:
                total_q += latest_metric.queue_length_m
        avg_q = total_q / len(non_brts_lanes)

        if avg_q > 70.0:
            one_hour_ago = now - datetime.timedelta(hours=1)
            existing = db.query(Recommendation).filter(
                Recommendation.junction_id == junction_id,
                Recommendation.issue_type == "queue_spillback",
                Recommendation.timestamp >= one_hour_ago
            ).first()

            if not existing:
                rec = Recommendation(
                    junction_id=junction_id,
                    timestamp=now,
                    issue_type="queue_spillback",
                    severity="critical",
                    description=f"Heavy queue spillback detected. Average junction queue is {avg_q:.1f}m, causing gridlock risk.",
                    suggested_action="Engage adaptive signal algorithm (Max-Pressure) to dynamically extend green cycle, or adjust fixed offsets along the corridor to achieve green-wave coordination.",
                    status="pending"
                )
                db.add(rec)
                db.commit()
                print(f"Recommendation logged: Queue Spillback at {junction_id}")
