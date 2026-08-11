from app.db import Base, engine, SessionLocal
from app.models import Junction, Lane

def seed_db():
    # Ensure all tables are created
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have junctions
        if db.query(Junction).count() > 0:
            print("Database: Tables verified. Seed data already exists.")
            return
            
        print("Database: Seeding initial Surat junctions, lanes, and spatial parameters...")
        
        # 1. Majura Gate Intersection (Center of Ring Road & BRTS)
        j1 = Junction(
            id="J001",
            name="Majura Gate Intersection",
            latitude=21.1788,
            longitude=72.8184,
            signal_mode="fixed",
            current_phase="Phase 1: North-South Green",
            cycle_length=120
        )
        
        l1_n = Lane(
            id="J001_L_N",
            junction_id="J001",
            lane_name="Northbound (Ring Road)",
            direction="N",
            is_brts=False,
            polygon_coords=[
                [21.1790, 72.8182], [21.1802, 72.8182], 
                [21.1802, 72.8184], [21.1790, 72.8184]
            ]
        )
        l1_s = Lane(
            id="J001_L_S",
            junction_id="J001",
            lane_name="Southbound (Ring Road)",
            direction="S",
            is_brts=False,
            polygon_coords=[
                [21.1774, 72.8184], [21.1786, 72.8184], 
                [21.1786, 72.8186], [21.1774, 72.8186]
            ]
        )
        l1_e = Lane(
            id="J001_L_E_BRTS",
            junction_id="J001",
            lane_name="Eastbound BRTS Corridor",
            direction="E",
            is_brts=True,
            polygon_coords=[
                [21.1786, 72.8186], [21.1786, 72.8198], 
                [21.1788, 72.8198], [21.1788, 72.8186]
            ]
        )
        l1_w = Lane(
            id="J001_L_W",
            junction_id="J001",
            lane_name="Westbound (Ring Road)",
            direction="W",
            is_brts=False,
            polygon_coords=[
                [21.1788, 72.8172], [21.1788, 72.8182], 
                [21.1790, 72.8182], [21.1790, 72.8172]
            ]
        )
        
        # 2. Sahara Darwaja Junction (High congestion near railway station)
        j2 = Junction(
            id="J002",
            name="Sahara Darwaja Junction",
            latitude=21.1963,
            longitude=72.8465,
            signal_mode="fixed",
            current_phase="Phase 1: East-West Green",
            cycle_length=120
        )
        
        l2_n = Lane(
            id="J002_L_N",
            junction_id="J002",
            lane_name="Northbound (Station Road)",
            direction="N",
            is_brts=False,
            polygon_coords=[
                [21.1965, 72.8463], [21.1977, 72.8463], 
                [21.1977, 72.8465], [21.1965, 72.8465]
            ]
        )
        l2_s = Lane(
            id="J002_L_S",
            junction_id="J002",
            lane_name="Southbound (Ring Road)",
            direction="S",
            is_brts=False,
            polygon_coords=[
                [21.1949, 72.8465], [21.1961, 72.8465], 
                [21.1961, 72.8467], [21.1949, 72.8467]
            ]
        )
        l2_e = Lane(
            id="J002_L_E",
            junction_id="J002",
            lane_name="Eastbound (Sahara Road)",
            direction="E",
            is_brts=False,
            polygon_coords=[
                [21.1961, 72.8467], [21.1961, 72.8479], 
                [21.1963, 72.8479], [21.1963, 72.8467]
            ]
        )
        l2_w = Lane(
            id="J002_L_W_BRTS",
            junction_id="J002",
            lane_name="Westbound BRTS Corridor",
            direction="W",
            is_brts=True,
            polygon_coords=[
                [21.1963, 72.8453], [21.1963, 72.8463], 
                [21.1965, 72.8463], [21.1965, 72.8453]
            ]
        )
        
        # 3. Athwa Gate Junction (Connects VIP Road, Athwalines)
        j3 = Junction(
            id="J003",
            name="Athwa Gate Junction",
            latitude=21.1895,
            longitude=72.8080,
            signal_mode="fixed",
            current_phase="Phase 1: North-South Green",
            cycle_length=120
        )
        
        l3_n = Lane(
            id="J003_L_N_BRTS",
            junction_id="J003",
            lane_name="Northbound BRTS Corridor",
            direction="N",
            is_brts=True,
            polygon_coords=[
                [21.1897, 72.8078], [21.1909, 72.8078], 
                [21.1909, 72.8080], [21.1897, 72.8080]
            ]
        )
        l3_s = Lane(
            id="J003_L_S",
            junction_id="J003",
            lane_name="Southbound (Athwa Road)",
            direction="S",
            is_brts=False,
            polygon_coords=[
                [21.1881, 72.8080], [21.1893, 72.8080], 
                [21.1893, 72.8082], [21.1881, 72.8082]
            ]
        )
        l3_e = Lane(
            id="J003_L_E",
            junction_id="J003",
            lane_name="Eastbound (Dumas Road)",
            direction="E",
            is_brts=False,
            polygon_coords=[
                [21.1893, 72.8082], [21.1893, 72.8094], 
                [21.1895, 72.8094], [21.1895, 72.8082]
            ]
        )
        l3_w = Lane(
            id="J003_L_W",
            junction_id="J003",
            lane_name="Westbound (Dumas Road)",
            direction="W",
            is_brts=False,
            polygon_coords=[
                [21.1894, 72.8068], [21.1894, 72.8078], 
                [21.1896, 72.8078], [21.1896, 72.8068]
            ]
        )
        
        db.add_all([j1, l1_n, l1_s, l1_e, l1_w])
        db.add_all([j2, l2_n, l2_s, l2_e, l2_w])
        db.add_all([j3, l3_n, l3_s, l3_e, l3_w])
        db.commit()
        print("Database: Seeding complete.")
    except Exception as e:
        print(f"Database: Seeding failed. Error: {e}")
        db.rollback()
    finally:
        db.close()
