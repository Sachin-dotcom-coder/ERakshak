import datetime
import random
from app.db import engine, SessionLocal, Base
from app.models import Junction, Lane, TrafficMetric, Violation, Recommendation

# Real Surat Junctions (22 Key Intersections across major corridors)
SURAT_JUNCTIONS_DATA = [
    {"id": "J001", "name": "Majura Gate Flyover", "latitude": 21.1825, "longitude": 72.8210, "zone": "Central Surat", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 45},
    {"id": "J002", "name": "Sahara Darwaja Junction", "latitude": 21.1965, "longitude": 72.8440, "zone": "Ring Road", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 50},
    {"id": "J003", "name": "Athwa Gate Circle", "latitude": 21.1750, "longitude": 72.8120, "zone": "Athwa Zone", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 40},
    {"id": "J004", "name": "Ring Road / Delhi Gate", "latitude": 21.2010, "longitude": 72.8360, "zone": "Ring Road", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 55},
    {"id": "J005", "name": "Adajan Gam / Patia", "latitude": 21.1980, "longitude": 72.7950, "zone": "West Zone", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 45},
    {"id": "J006", "name": "Piplod Junction", "latitude": 21.1540, "longitude": 72.7750, "zone": "Dumas Road", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 40},
    {"id": "J007", "name": "Varachha / Sardar Chowk", "latitude": 21.2180, "longitude": 72.8620, "zone": "East Zone", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 60},
    {"id": "J008", "name": "Udhna Darwaja", "latitude": 21.1680, "longitude": 72.8390, "zone": "Udhna Corridor", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 45},
    {"id": "J009", "name": "Khatodara GIDC Cross", "latitude": 21.1620, "longitude": 72.8250, "zone": "Industrial Corridor", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 50},
    {"id": "J010", "name": "Katargam Darwaja", "latitude": 21.2150, "longitude": 72.8280, "zone": "North Zone", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 45},
    {"id": "J011", "name": "Vesu VIP Road Crossing", "latitude": 21.1410, "longitude": 72.7820, "zone": "Vesu Zone", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 40},
    {"id": "J012", "name": "Dindoli Bridge Approach", "latitude": 21.1550, "longitude": 72.8650, "zone": "South-East Zone", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 45},
    {"id": "J013", "name": "Kamrej Highway Junction", "latitude": 21.2680, "longitude": 72.9550, "zone": "Outer Ring Road", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 60},
    {"id": "J014", "name": "Textile Market Corridor", "latitude": 21.1900, "longitude": 72.8490, "zone": "Commercial Hub", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 55},
    {"id": "J015", "name": "Palanpur Jakatnaka", "latitude": 21.2120, "longitude": 72.7830, "zone": "Rander Zone", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 45},
    {"id": "J016", "name": "Sarthana Jakatnaka", "latitude": 21.2310, "longitude": 72.9010, "zone": "East Zone", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 50},
    {"id": "J017", "name": "Cable Bridge Adajan Side", "latitude": 21.1890, "longitude": 72.8050, "zone": "Tapi River Crossing", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 40},
    {"id": "J018", "name": "Gopipura Main Road", "latitude": 21.1950, "longitude": 72.8220, "zone": "Heritage Zone", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 35},
    {"id": "J019", "name": "Bhatar Char Rasta", "latitude": 21.1610, "longitude": 72.8110, "zone": "Bhatar Zone", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 45},
    {"id": "J020", "name": "Althan Canal Road", "latitude": 21.1480, "longitude": 72.8090, "zone": "Althan Zone", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 40},
    {"id": "J021", "name": "Ichhapore GIDC Cross", "latitude": 21.1710, "longitude": 72.7210, "zone": "Hazira Belt", "signal_mode": "adaptive", "current_phase": "NS_GREEN", "cycle_length": 50},
    {"id": "J022", "name": "Dumas Beach Approach", "latitude": 21.0850, "longitude": 72.7120, "zone": "Dumas Coastal", "signal_mode": "adaptive", "current_phase": "EW_GREEN", "cycle_length": 35},
]

VIOLATION_TYPES = ["brts_intrusion", "lane_violation", "wrong_side_entry"]
VEHICLE_TYPES = ["car", "auto", "motorcycle", "truck", "suv"]
ISSUES = [
    ("brts_intrusion", "Active vehicle detected in BRTS dedicated lane. Adjust cycle or alert traffic police."),
    ("asymmetric_flow", "Northbound queue is 3.2x Southbound. Extend North-South green phase by +12s."),
    ("queue_spillback", "Queue length exceeded 80m. Signal cycle increased to prevent gridlock."),
]

def seed_database():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Junctions & Lanes
        existing_j_ids = {j.id for j in db.query(Junction.id).all()}
        for j_data in SURAT_JUNCTIONS_DATA:
            j_id = j_data["id"]
            if j_id not in existing_j_ids:
                j_obj = Junction(
                    id=j_id,
                    name=j_data["name"],
                    latitude=j_data["latitude"],
                    longitude=j_data["longitude"],
                    signal_mode=j_data["signal_mode"],
                    current_phase=j_data["current_phase"],
                    cycle_length=j_data["cycle_length"]
                )
                db.add(j_obj)
                db.commit()

                # Add 4 lanes per junction (including BRTS lane)
                directions = ["N", "S", "E", "W"]
                for i, d in enumerate(directions):
                    is_brts = (i == 0) # North lane is designated BRTS corridor
                    l_obj = Lane(
                        id=f"{j_id}_lane_{d}",
                        junction_id=j_id,
                        lane_name=f"{j_data['name']} - {'BRTS' if is_brts else 'Standard'} ({d})",
                        direction=d,
                        is_brts=is_brts
                    )
                    db.add(l_obj)
                db.commit()

        print("Seeded 22 Surat Junctions and 88 Lanes successfully.")

        # 2. Seed Historical Violations
        violation_count = db.query(Violation).count()
        if violation_count < 15:
            now = datetime.datetime.utcnow()
            for i in range(25):
                j_data = random.choice(SURAT_JUNCTIONS_DATA)
                v_type = random.choice(VIOLATION_TYPES)
                v_obj = Violation(
                    lane_id=f"{j_data['id']}_lane_N",
                    timestamp=now - datetime.timedelta(minutes=random.randint(5, 180)),
                    violation_type=v_type,
                    vehicle_type=random.choice(VEHICLE_TYPES),
                    snapshot_url=f"/snapshots/{v_type}_{i+100}.jpg"
                )
                db.add(v_obj)
            db.commit()
            print("Seeded historical BRTS violations.")

        # 3. Seed Predictive Recommendations
        rec_count = db.query(Recommendation).count()
        if rec_count < 10:
            for j_data in SURAT_JUNCTIONS_DATA[:8]:
                issue, action = random.choice(ISSUES)
                r_obj = Recommendation(
                    junction_id=j_data["id"],
                    issue_type=issue,
                    severity="critical" if issue == "brts_intrusion" else "warning",
                    description=f"Traffic anomaly detected at {j_data['name']}.",
                    suggested_action=action,
                    status="pending",
                    timestamp=datetime.datetime.utcnow() - datetime.timedelta(minutes=random.randint(2, 60))
                )
                db.add(r_obj)
            db.commit()
            print("Seeded predictive recommendations.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
