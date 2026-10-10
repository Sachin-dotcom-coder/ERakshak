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
    "Phase 1: Northbound Protected Green",
    "Phase 2: Eastbound Protected Green",
    "Phase 3: Southbound Protected Green",
    "Phase 4: Westbound / BRTS Protected Green"
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
    
    # Preserving historical logs
    adaptive_controller_state = {}

    try:
        while True:
            junctions = db.query(Junction).all()
            for junction in junctions:
                # Check if junction is actively receiving live Vision Service events (within last 15s)
                latest_live_metric = db.query(TrafficMetric).join(Lane).filter(
                    Lane.junction_id == junction.id
                ).order_by(TrafficMetric.timestamp.desc()).first()

                if latest_live_metric and (datetime.datetime.utcnow() - latest_live_metric.timestamp).total_seconds() < 15:
                    # Skip mock simulation for this junction — let live Vision Service drive it!
                    continue

                # 1. Manage signal phases based on mode

                # Initialize junction controller state if needed
                if junction.id not in phase_counters:
                    phase_counters[junction.id] = 0
                if junction.id not in adaptive_controller_state:
                    # Initialize with North or West, 0 ticks held, and balanced wait times
                    adaptive_controller_state[junction.id] = {
                        "current_arm": "N",
                        "ticks_held": 0,
                        "allocated_ticks": 6,  # 12 seconds initial
                        "wait_ticks": {"N": 0, "S": 2, "E": 4, "W": 6}
                    }

                ctrl = adaptive_controller_state[junction.id]

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
                    # --- REAL MAX-PRESSURE CONTROLLER WITH MIN-GREEN (>=10s) & STARVATION PREVENTION ---
                    MIN_GREEN_TICKS = 5   # At least 10 seconds green before switching
                    MAX_GREEN_TICKS = 15  # At most 30 seconds max green to avoid starvation

                    ctrl["ticks_held"] += 1

                    # Increment red waiting ticks for all non-green arms to track starvation
                    for d in ["N", "S", "E", "W"]:
                        if d != ctrl["current_arm"]:
                            ctrl["wait_ticks"][d] = ctrl["wait_ticks"].get(d, 0) + 1

                    # Gather latest queue per direction
                    dir_queues = {"N": 15.0, "S": 15.0, "E": 15.0, "W": 15.0}
                    dir_lanes = {}
                    for lane in junction.lanes:
                        latest_m = db.query(TrafficMetric).filter(
                            TrafficMetric.lane_id == lane.id
                        ).order_by(TrafficMetric.timestamp.desc()).first()
                        q_val = latest_m.queue_length_m if latest_m else 20.0
                        dir_queues[lane.direction] = max(dir_queues.get(lane.direction, 0.0), q_val)
                        if lane.direction not in dir_lanes:
                            dir_lanes[lane.direction] = lane

                    current_arm = ctrl["current_arm"]
                    current_queue = dir_queues.get(current_arm, 0.0)

                    # Check if phase change is permissible
                    can_switch = False
                    if ctrl["ticks_held"] >= ctrl["allocated_ticks"]:
                        can_switch = True
                    elif ctrl["ticks_held"] >= MIN_GREEN_TICKS and current_queue < 5.0:
                        # Queue cleared before allocated time: cut green early to save cycle time
                        can_switch = True
                    elif ctrl["ticks_held"] >= MAX_GREEN_TICKS:
                        # Forced switch to prevent cross-traffic gridlock
                        can_switch = True

                    if can_switch:
                        # Calculate starvation-weighted pressure score for every arm:
                        # Pressure = Queue Length + (Red Wait Seconds * Starvation Factor)
                        scores = {}
                        for d in ["N", "E", "S", "W"]:
                            if d == current_arm and ctrl["ticks_held"] >= MIN_GREEN_TICKS:
                                # Penalize recently serviced arm slightly to give waiting arms a turn
                                scores[d] = dir_queues.get(d, 0.0) * 0.7
                            else:
                                wait_seconds = ctrl["wait_ticks"].get(d, 0) * 2.0
                                # Starvation weight: after 20s of waiting, adds +30 pressure!
                                scores[d] = dir_queues.get(d, 0.0) + (wait_seconds * 1.5)

                        # Select highest pressure arm
                        best_arm = max(scores.keys(), key=lambda d: scores[d])

                        if best_arm != current_arm:
                            ctrl["current_arm"] = best_arm
                            ctrl["ticks_held"] = 0
                            ctrl["wait_ticks"][best_arm] = 0
                            # Dynamically allocate green duration based on incoming queue (10s to 26s)
                            best_q = dir_queues.get(best_arm, 20.0)
                            allocated_secs = min(30, max(10, round(10 + best_q * 0.25)))
                            ctrl["allocated_ticks"] = max(MIN_GREEN_TICKS, round(allocated_secs / 2))
                            junction.cycle_length = allocated_secs

                    dir_name = {
                        "N": "Northbound", "S": "Southbound",
                        "E": "Eastbound", "W": "Westbound"
                    }.get(ctrl["current_arm"], "Northbound")
                    junction.current_phase = f"Adaptive: {dir_name} Green Priority"
                    db.commit()

                # 2. Simulate Traffic Metrics for each lane of this junction
                total_vehicles = 0
                total_queue = 0.0
                lanes_data = []

                active_dir = ctrl["current_arm"] if junction.signal_mode != "fixed" else None
                if junction.signal_mode == "fixed":
                    if "North" in junction.current_phase: active_dir = "N"
                    elif "East" in junction.current_phase: active_dir = "E"
                    elif "South" in junction.current_phase: active_dir = "S"
                    elif "West" in junction.current_phase: active_dir = "W"

                for lane in junction.lanes:
                    is_green = (lane.direction == active_dir)

                    # Fetch latest metric to iterate smoothly
                    prev = db.query(TrafficMetric).filter(
                        TrafficMetric.lane_id == lane.id
                    ).order_by(TrafficMetric.timestamp.desc()).first()

                    prev_count = prev.vehicle_count if prev else random.randint(12, 22)
                    prev_queue = prev.queue_length_m if prev else random.uniform(20.0, 35.0)

                    if is_green:
                        # Green phase: discharge waiting queue smoothly
                        v_count = max(3, prev_count - random.randint(2, 5) + random.randint(1, 2))
                        q_length = max(2.0, prev_queue - random.uniform(6.0, 12.0) + random.uniform(1.0, 3.0))
                        avg_speed = max(28.0, 42.0 - (q_length * 0.15) + random.uniform(-2.0, 2.0))
                    else:
                        # Red phase: accumulate arriving queue
                        v_count = min(42, prev_count + random.randint(1, 3))
                        q_length = min(110.0, prev_queue + random.uniform(3.0, 6.0))
                        avg_speed = max(4.0, 24.0 - (q_length * 0.18) + random.uniform(-1.5, 1.5))

                    # Road Density (occupancy ratio): percentage of road storage capacity occupied
                    occupancy = min(0.95, max(0.12, q_length / 110.0))

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

            # 6. Database Housekeeping: Delete metrics older than 90 days to retain historical reports
            threshold = datetime.datetime.utcnow() - datetime.timedelta(days=90)
            db.query(TrafficMetric).filter(TrafficMetric.timestamp < threshold).delete()
            db.commit()

            await asyncio.sleep(2.0)
            
    except asyncio.CancelledError:
        print("Mock Generator: Loop cancelled.")
    except Exception as e:
        print(f"Mock Generator error: {e}")
    finally:
        db.close()
