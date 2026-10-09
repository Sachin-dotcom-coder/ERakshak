import datetime
from sqlalchemy.orm import Session
from app.models import Junction, Recommendation, Violation, TrafficMetric, Lane
from app.event_bus import event_bus

async def run_recommendation_engine(db: Session, junction_id: str):
    """
    Analyzes recent metrics and violations for a junction,
    and logs engineering recommendations if thresholds are crossed.
    """
    now = datetime.datetime.utcnow()
    ten_minutes_ago = now - datetime.timedelta(minutes=10)

    # Resolve junction name for logging/publishing
    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    junction_name = junction.name if junction else "Unknown Junction"

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
                    description=f"🚨 Multiple cars entering BRTS Bus Lane ({intrusion_count} vehicles in 10 mins) on {lane.lane_name}.",
                    suggested_action=f"Deploy a traffic police officer or place traffic cones at the entrance of {lane.lane_name} to stop private cars.",
                    status="pending"
                )
                db.add(rec)
                db.commit()
                print(f"Recommendation logged: BRTS Intrusion Heavy at {junction_id}")

                await event_bus.publish("traffic_live_events", {
                    "type": "new_recommendation",
                    "id": rec.id,
                    "junction_id": junction_id,
                    "junction_name": junction_name,
                    "timestamp": rec.timestamp.isoformat(),
                    "issue_type": rec.issue_type,
                    "severity": rec.severity,
                    "description": rec.description,
                    "suggested_action": rec.suggested_action,
                    "status": rec.status
                })

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
                    description=f"🟢 Heavy traffic backlog in {heavy_dir} direction ({max(n_q, s_q):.0f}m queue) vs {light_dir}.",
                    suggested_action=f"Extend {heavy_dir} green light time by +12s or open an extra lane to clear the traffic queue.",
                    status="pending"
                )
                db.add(rec)
                db.commit()
                print(f"Recommendation logged: Asymmetric Flow at {junction_id}")

                await event_bus.publish("traffic_live_events", {
                    "type": "new_recommendation",
                    "id": rec.id,
                    "junction_id": junction_id,
                    "junction_name": junction_name,
                    "timestamp": rec.timestamp.isoformat(),
                    "issue_type": rec.issue_type,
                    "severity": rec.severity,
                    "description": rec.description,
                    "suggested_action": rec.suggested_action,
                    "status": rec.status
                })

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
                    description=f"🚦 High traffic queue ({avg_q:.0f}m) creating risk of road junction jam.",
                    suggested_action="Increase green light cycle time by +15s to clear queued traffic before gridlock forms.",
                    status="pending"
                )
                db.add(rec)
                db.commit()
                print(f"Recommendation logged: Queue Spillback at {junction_id}")

                await event_bus.publish("traffic_live_events", {
                    "type": "new_recommendation",
                    "id": rec.id,
                    "junction_id": junction_id,
                    "junction_name": junction_name,
                    "timestamp": rec.timestamp.isoformat(),
                    "issue_type": rec.issue_type,
                    "severity": rec.severity,
                    "description": rec.description,
                    "suggested_action": rec.suggested_action,
                    "status": rec.status
                })
