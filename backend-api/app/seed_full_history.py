import datetime
import random
from app.db import Base, engine, SessionLocal
from app.models import Junction, Lane, TrafficMetric, Violation, Recommendation
from app.seed_db import SURAT_JUNCTIONS_DATA

def run_rich_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    now = datetime.datetime.now(datetime.timezone.utc)

    # 1. Ensure all 22 Surat Junctions exist
    existing_junc_ids = {j.id for j in db.query(Junction.id).all()}
    for j in SURAT_JUNCTIONS_DATA:
        if j['id'] not in existing_junc_ids:
            db.add(Junction(
                id=j['id'],
                name=j['name'],
                latitude=j['latitude'],
                longitude=j['longitude'],
                signal_mode=j.get('signal_mode', 'adaptive'),
                current_phase=j.get('current_phase', 'NS_GREEN'),
                cycle_length=j.get('cycle_length', 50)
            ))
    db.commit()

    # 2. Ensure all 4 lanes exist per junction
    existing_lane_ids = {l.id for l in db.query(Lane.id).all()}
    for j in SURAT_JUNCTIONS_DATA:
        jid = j['id']
        for d, is_brts in [('N', True), ('S', False), ('E', False), ('W', False)]:
            lid = f"{jid}_lane_{d}"
            if lid not in existing_lane_ids:
                label = "BRTS Corridor" if is_brts else "Standard Lane"
                db.add(Lane(
                    id=lid,
                    junction_id=jid,
                    lane_name=f"{j['name']} - {label} ({d})",
                    direction=d,
                    is_brts=is_brts
                ))
    db.commit()

    all_lanes = db.query(Lane).all()
    brts_lanes = [l for l in all_lanes if l.is_brts]

    # 3. Seed 600+ Violations across past 60 days
    V_TYPES = ['brts_intrusion', 'brts_intrusion', 'lane_violation', 'signal_jump', 'wrong_side_entry']
    V_VEHICLES = ['two-wheeler', 'auto', 'car', 'auto', 'two-wheeler', 'truck', 'suv']

    # Delete existing low-count violations to ensure uniform 60-day distribution
    db.query(Violation).delete()
    db.commit()

    # Generate violations for every single day in the last 60 days
    for day_offset in range(60):
        day_date = now - datetime.timedelta(days=day_offset)
        daily_count = random.randint(8, 22)  # 8-22 violations per day
        for _ in range(daily_count):
            hour = random.choices([8, 9, 10, 11, 14, 17, 18, 19, 20, 21], weights=[10, 15, 12, 8, 6, 12, 18, 15, 10, 5])[0]
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            v_time = day_date.replace(hour=hour, minute=minute, second=second, microsecond=0)
            v_type = random.choice(V_TYPES)
            veh = random.choice(V_VEHICLES)
            target_lane = random.choice(brts_lanes) if 'brts' in v_type else random.choice(all_lanes)
            db.add(Violation(
                lane_id=target_lane.id,
                timestamp=v_time.replace(tzinfo=None),
                violation_type=v_type,
                vehicle_type=veh,
                snapshot_url=f"/snapshots/{v_type}_{veh}_{day_offset}_{hour}.jpg"
            ))
    db.commit()

    # 4. Seed Traffic Metrics across past 60 days (4 snapshots per day across junctions)
    db.query(TrafficMetric).delete()
    db.commit()

    top_junctions = SURAT_JUNCTIONS_DATA[:12]
    top_lanes = [l for l in all_lanes if any(l.junction_id == j['id'] for j in top_junctions)]

    for day_offset in range(60):
        day_date = now - datetime.timedelta(days=day_offset)
        for hour in [9, 13, 18, 21]:
            m_time = day_date.replace(hour=hour, minute=30, second=0, microsecond=0)
            for lane in top_lanes:
                is_peak = hour in (9, 18)
                base_q = random.uniform(35.0, 78.0) if is_peak else random.uniform(12.0, 36.0)
                base_speed = random.uniform(16.0, 26.0) if is_peak else random.uniform(32.0, 48.0)
                veh_count = random.randint(30, 75) if is_peak else random.randint(12, 32)
                db.add(TrafficMetric(
                    lane_id=lane.id,
                    timestamp=m_time.replace(tzinfo=None),
                    vehicle_count=veh_count,
                    queue_length_m=round(base_q, 1),
                    average_speed_kmh=round(base_speed, 1),
                    occupancy_ratio=round(min(0.98, base_q / 85.0), 2)
                ))
    db.commit()

    # 5. Seed Recommendations
    db.query(Recommendation).delete()
    REC_TEMPLATES = [
        ('J001', 'brts_intrusion_heavy', 'critical', 'Repeated two-wheeler intrusion on Ring Road BRTS approach during evening rush.', 'Deploy automated ANPR enforcement barricade and assign traffic warden.', 'pending'),
        ('J002', 'queue_spillback', 'high', 'Southbound queue exceeds 72m on Sahara Darwaja causing gridlock on textile market ramp.', 'Increase North-South split by +14 seconds in Phase 2 adaptive cycle.', 'applied'),
        ('J003', 'asymmetric_flow', 'medium', 'Athwa Gate Circle inbound flow is 2.8x outbound flow during morning office hours.', 'Coordinate green wave offset with Majura Gate intersection (+18s lead).', 'pending'),
        ('J004', 'queue_spillback', 'high', 'Delhi Gate queue spillback detected towards railway station approach.', 'Enable dynamic queue flush phase on Eastbound approach.', 'applied'),
        ('J007', 'brts_intrusion_heavy', 'critical', 'Heavy mixed auto-rickshaw intrusions into Varachha BRTS corridor.', 'Issue automated challans via Surat Smart City camera integration.', 'pending'),
        ('J008', 'queue_spillback', 'medium', 'Udhna Darwaja BRTS crossing congestion spike during industrial shift change.', 'Extend dedicated BRTS green priority signal by 8 seconds.', 'pending'),
        ('J014', 'congestion_bottleneck', 'high', 'Commercial freight loading spilling over to Textile Market arterial lanes.', 'Enforce strict no-stopping zone between 17:00 and 21:00.', 'pending'),
        ('J005', 'queue_spillback', 'medium', 'Adajan Gam approach queue build-up during evening bridge traffic.', 'Implement dynamic cycle length extension up to 135s.', 'applied'),
        ('J006', 'asymmetric_flow', 'low', 'Piplod Junction weekend tourist flow towards Dumas Road.', 'Deploy automated weekend timing plan with +12s green on Dumas approach.', 'pending'),
        ('J017', 'queue_spillback', 'high', 'Cable Bridge Adajan ramp bottleneck during morning commute peak.', 'Coordinate with Adajan Gam signal to throttle incoming flow.', 'pending')
    ]

    for jid, itype, sev, desc, action, status in REC_TEMPLATES:
        db.add(Recommendation(
            junction_id=jid,
            timestamp=(now - datetime.timedelta(days=random.randint(1, 20))).replace(tzinfo=None),
            issue_type=itype,
            severity=sev,
            description=desc,
            suggested_action=action,
            status=status
        ))
    db.commit()

    print("RICH SEEDING COMPLETE!")
    print(f"Junctions: {db.query(Junction).count()}")
    print(f"Lanes: {db.query(Lane).count()}")
    print(f"Violations: {db.query(Violation).count()}")
    print(f"Metrics: {db.query(TrafficMetric).count()}")
    print(f"Recommendations: {db.query(Recommendation).count()}")
    db.close()

if __name__ == "__main__":
    run_rich_seed()
