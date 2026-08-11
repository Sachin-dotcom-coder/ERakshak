import asyncio
import random
import datetime
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Junction, Lane, TrafficMetric, Violation, Recommendation
from app.event_bus import event_bus
from app.recommendations import run_recommendation_engine

import sys
import os
from pathlib import Path

# Add signal-optimizer to sys.path so MaxPressureController can be imported
optimizer_path = Path(__file__).resolve().parent.parent.parent / "signal-optimizer"
if str(optimizer_path) not in sys.path:
    sys.path.insert(0, str(optimizer_path))

try:
    from max_pressure import MaxPressureController
except ImportError:
    MaxPressureController = None

# Surat vehicle configurations
VEHICLES = ["auto", "motorcycle", "car", "suv", "citybus", "truck"]
VIOLATION_VEHICLES = ["auto", "motorcycle", "car", "suv"]
PHASES = [
    "Phase 1: North-South Green",
    "Phase 2: North-South Left Turn",
    "Phase 3: East-West Green",
    "Phase 4: East-West Left Turn"
]

async def start_mock_traffic_loop():
    """
    Simulates real-time vehicle flow, signal optimization, and lane intrusion violations.
    Runs inside the FastAPI event loop.
    """
    print("Mock Generator: Starting mock traffic generation loop...")
    db: Session = SessionLocal()
    
    # We maintain in-memory counters to cycle phases if junctions are in 'fixed' mode
    phase_counters = {}
    
    # Clear out old metrics, violations, and recs on fresh start to keep the demo clean
    db.query(TrafficMetric).delete()
    db.query(Violation).delete()
    db.query(Recommendation).delete()
    db.commit()

    try:
        while True:
            junctions = db.query(Junction).all()
            for junction in junctions:
                # 1. Manage signal phases based on mode
                if junction.id not in phase_counters:
                    phase_counters[junction.id] = 0

                if junction.signal_mode == "fixed":
                    # Cycle phases sequentially every 10 iterations (20 seconds)
                    phase_counters[junction.id] += 1
                    if phase_counters[junction.id] >= 10:
                        phase_counters[junction.id] = 0
                        current_phase_idx = PHASES.index(junction.current_phase) if junction.current_phase in PHASES else 0
                        next_phase_idx = (current_phase_idx + 1) % len(PHASES)
                        junction.current_phase = PHASES[next_phase_idx]
                        db.commit()
                else:
                    # Adaptive Mode: Apply simplified Max-Pressure logic.
                    # Direct the green phase toward the lane with the longest queue.
                    max_queue_lane = None
                    max_queue = -1.0
                    for lane in junction.lanes:
                        if lane.is_brts:
                            continue
                        # Get latest queue length
                        latest_m = db.query(TrafficMetric).filter(
                            TrafficMetric.lane_id == lane.id
                        ).order_by(TrafficMetric.timestamp.desc()).first()
                        if latest_m and latest_m.queue_length_m > max_queue:
                            max_queue = latest_m.queue_length_m
                            max_queue_lane = lane
                    
                    if max_queue_lane:
                        dir_name = {
                            "N": "Northbound", "S": "Southbound",
                            "E": "Eastbound", "W": "Westbound"
                        }.get(max_queue_lane.direction, "Northbound")
                        junction.current_phase = f"Adaptive: {dir_name} Green Priority"
                        db.commit()

                # 2. Simulate Traffic Metrics for each lane of this junction
                total_vehicles = 0
                total_queue = 0.0
                lanes_data = []

                for lane in junction.lanes:
                    # BRTS lanes have low standard traffic unless there is a BRTS bus
                    if lane.is_brts:
                        # 3% chance a BRTS bus is passing through legally
                        has_bus = random.random() < 0.03
                        v_count = 1 if has_bus else 0
                        q_length = 0.0
                        occupancy = 0.05 if has_bus else 0.0
                        avg_speed = 45.0 + random.uniform(-5.0, 5.0) if has_bus else 60.0
                    else:
                        # Regular lanes fluctuate dynamically
                        # If green phase matches direction, drain queue, else build queue
                        is_green = False
                        if "Green" in junction.current_phase or "Priority" in junction.current_phase:
                            # Simple match: check if the direction letter is in the phase text
                            dir_fullname = {"N": "North", "S": "South", "E": "East", "W": "West"}.get(lane.direction)
                            if dir_fullname and dir_fullname in junction.current_phase:
                                is_green = True
                        
                        # Fetch latest metric to iterate from it
                        prev = db.query(TrafficMetric).filter(
                            TrafficMetric.lane_id == lane.id
                        ).order_by(TrafficMetric.timestamp.desc()).first()

                        prev_count = prev.vehicle_count if prev else random.randint(10, 20)
                        prev_queue = prev.queue_length_m if prev else random.uniform(15.0, 30.0)

                        if is_green:
                            # Drain queue
                            v_count = max(2, prev_count - random.randint(3, 7) + random.randint(1, 3))
                            q_length = max(0.0, prev_queue - random.uniform(5.0, 15.0) + random.uniform(1.0, 4.0))
                            avg_speed = max(25.0, 40.0 - (q_length * 0.2) + random.uniform(-3.0, 3.0))
                        else:
                            # Accumulate queue
                            v_count = min(45, prev_count + random.randint(1, 4))
                            q_length = min(120.0, prev_queue + random.uniform(2.0, 8.0))
                            avg_speed = max(2.0, 25.0 - (q_length * 0.2) + random.uniform(-2.0, 2.0))

                        occupancy = min(1.0, q_length / 120.0)

                    # Create and store metric
                    metric = TrafficMetric(
                        lane_id=lane.id,
                        timestamp=datetime.datetime.utcnow(),
                        vehicle_count=v_count,
                        queue_length_m=round(q_length, 1),
                        occupancy_ratio=round(occupancy, 2),
                        average_speed_kmh=round(avg_speed, 1)
                    )
                    db.add(metric)
                    db.commit()

                    total_vehicles += v_count
                    total_queue += q_length
                    
                    lanes_data.append({
                        "lane_id": lane.id,
                        "lane_name": lane.lane_name,
                        "direction": lane.direction,
                        "is_brts": lane.is_brts,
                        "polygon_coords": lane.polygon_coords,
                        "vehicle_count": v_count,
                        "queue_length_m": round(q_length, 1),
                        "occupancy_ratio": round(occupancy, 2),
                        "average_speed_kmh": round(avg_speed, 1)
                    })

                # Calculate averages
                avg_q = total_queue / len(junction.lanes) if junction.lanes else 0.0

                # 3. Simulate BRTS lane intrusions (Violations)
                # Occurs with 3% probability on BRTS lanes per junction per tick
                brts_lanes = [l for l in junction.lanes if l.is_brts]
                for bl in brts_lanes:
                    if random.random() < 0.03:
                        vehicle = random.choice(VIOLATION_VEHICLES)
                        violation = Violation(
                            lane_id=bl.id,
                            timestamp=datetime.datetime.utcnow(),
                            violation_type="brts_intrusion",
                            vehicle_type=vehicle,
                            snapshot_url=f"/snapshots/intrusion_{vehicle}_{random.randint(100,999)}.jpg"
                        )
                        db.add(violation)
                        db.commit()
                        
                        print(f"Violation: {vehicle} intruded BRTS corridor at {junction.name}")

                        # Push immediate violation event to EventBus
                        await event_bus.publish("traffic_live_events", {
                            "type": "new_violation",
                            "id": violation.id,
                            "lane_id": violation.lane_id,
                            "timestamp": violation.timestamp.isoformat(),
                            "violation_type": violation.violation_type,
                            "vehicle_type": violation.vehicle_type,
                            "snapshot_url": violation.snapshot_url,
                            "lane_name": bl.lane_name,
                            "junction_name": junction.name
                        })

                # 4. Run rule-based recommendations engine
                await run_recommendation_engine(db, junction.id)
                
                # Fetch recommendations to send count of current active ones
                active_recs = db.query(Recommendation).filter(
                    Recommendation.junction_id == junction.id, 
                    Recommendation.status == "pending"
                ).all()

                # Fetch recent BRTS intrusions in last 10 mins
                ten_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
                brts_intrusion_count = db.query(Violation).join(Lane).filter(
                    Lane.junction_id == junction.id,
                    Violation.violation_type == "brts_intrusion",
                    Violation.timestamp >= ten_mins_ago
                ).count()

                # 5. Publish Junction live update to EventBus
                await event_bus.publish("traffic_live_events", {
                    "type": "junction_update",
                    "junction_id": junction.id,
                    "name": junction.name,
                    "latitude": junction.latitude,
                    "longitude": junction.longitude,
                    "signal_mode": junction.signal_mode,
                    "current_phase": junction.current_phase,
                    "cycle_length": junction.cycle_length,
                    "total_vehicles": total_vehicles,
                    "avg_queue_length_m": round(avg_q, 1),
                    "brts_intrusion_count": brts_intrusion_count,
                    "active_recommendations_count": len(active_recs),
                    "lanes": lanes_data
                })

            # 6. Database Housekeeping: Delete metrics older than 30 mins to avoid infinite table growth
            threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
            db.query(TrafficMetric).filter(TrafficMetric.timestamp < threshold).delete()
            db.commit()

            await asyncio.sleep(2.0)
            
    except asyncio.CancelledError:
        print("Mock Generator: Loop cancelled.")
    except Exception as e:
        print(f"Mock Generator error: {e}")
    finally:
        db.close()
