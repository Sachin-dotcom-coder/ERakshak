import asyncio
import csv
import datetime
from io import StringIO
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, WebSocket, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db, SessionLocal
from app.models import Junction, Lane, TrafficMetric, Violation, Recommendation
from app.seed import seed_db
from app.mock_generator import start_mock_traffic_loop
from app.event_bus import event_bus
from app.report_generator import generate_pdf_report
from app.schemas import Junction as JunctionSchema

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize tables and seed data
    seed_db()
    # 2. Start the background simulation loop
    bg_task = asyncio.create_task(start_mock_traffic_loop())
    yield
    # 3. Clean up task on shutdown
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        print("Lifespan: Background simulation task successfully cancelled.")

app = FastAPI(
    title="E-Rakshak Traffic Optimization API",
    description="Adaptive signal control, BRTS intrusion monitoring, and predictive recommendation engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for the React development frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon/development convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "E-Rakshak Adaptive Traffic Management",
        "api_docs": "/docs"
    }

# --- REST ENDPOINTS ---

@app.get("/api/junctions", response_model=List[JunctionSchema])
def get_junctions(db: Session = Depends(get_db)):
    """Returns a list of all junctions with their constituent lanes."""
    return db.query(Junction).all()

@app.put("/api/junctions/{junction_id}/mode")
def update_junction_mode(junction_id: str, mode: str, db: Session = Depends(get_db)):
    """Toggles the optimization mode of a junction (fixed-timer vs adaptive)."""
    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    if not junction:
        raise HTTPException(status_code=404, detail="Junction not found")
    
    if mode.lower() not in ["fixed", "adaptive"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'fixed' or 'adaptive'")
    
    junction.signal_mode = mode.lower()
    
    # Immediately change current phase visual indicator
    if mode.lower() == "adaptive":
        junction.current_phase = "Adaptive: Priority Flow Detection Active"
    else:
        junction.current_phase = "Phase 1: North-South Green"
        
    db.commit()
    return {
        "junction_id": junction_id,
        "name": junction.name,
        "signal_mode": junction.signal_mode,
        "current_phase": junction.current_phase
    }

@app.get("/api/violations")
def get_violations(limit: int = 50, db: Session = Depends(get_db)):
    """Fetches the latest logged traffic and BRTS corridor violations."""
    violations = db.query(Violation).order_by(Violation.timestamp.desc()).limit(limit).all()
    result = []
    for v in violations:
        lane = db.query(Lane).filter(Lane.id == v.lane_id).first()
        j_name = db.query(Junction).filter(Junction.id == lane.junction_id).first().name if lane else "Unknown"
        result.append({
            "id": v.id,
            "lane_id": v.lane_id,
            "lane_name": lane.lane_name if lane else "Unknown Lane",
            "junction_name": j_name,
            "timestamp": v.timestamp.isoformat(),
            "violation_type": v.violation_type,
            "vehicle_type": v.vehicle_type,
            "snapshot_url": v.snapshot_url
        })
    return result

@app.get("/api/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    """Fetches logged predictive infrastructure recommendations."""
    recs = db.query(Recommendation).order_by(Recommendation.timestamp.desc()).all()
    result = []
    for r in recs:
        j_name = db.query(Junction).filter(Junction.id == r.junction_id).first().name
        result.append({
            "id": r.id,
            "junction_id": r.junction_id,
            "junction_name": j_name,
            "timestamp": r.timestamp.isoformat(),
            "issue_type": r.issue_type,
            "severity": r.severity,
            "description": r.description,
            "suggested_action": r.suggested_action,
            "status": r.status
        })
    return result

@app.put("/api/recommendations/{rec_id}/status")
def update_recommendation_status(rec_id: int, status: str, db: Session = Depends(get_db)):
    """Updates status of recommendation (e.g. marking it 'applied' or 'dismissed')."""
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    if status.lower() not in ["pending", "applied", "dismissed"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'pending', 'applied', or 'dismissed'")
        
    rec.status = status.lower()
    db.commit()
    return {"id": rec_id, "status": rec.status}

@app.get("/api/metrics/compare/{junction_id}")
def get_performance_comparison(junction_id: str):
    """
    Returns comparative performance curves (Vite frontend What-If plot).
    Simulates SUMO simulation steps comparing Fixed cycles vs Adaptive pressure cycles.
    """
    # Verify junction exists in database
    db = SessionLocal()
    j = db.query(Junction).filter(Junction.id == junction_id).first()
    db.close()
    if not j:
        raise HTTPException(status_code=404, detail="Junction not found")

    data = []
    # Generate 10 simulation steps showing wait times accumulating under fixed timing,
    # and staying optimized under adaptive pressure formula.
    for step in range(10, 110, 10):
        # Fixed wait times grow as vehicles queue up (simulated peak hour load)
        fixed_wait = float(15 + (step * 0.45) + (10 if junction_id == "J002" else 5))
        # Adaptive wait times flatten out due to dynamic green allocation
        adaptive_wait = float(14 + (step * 0.08) + (1 if step > 50 else 0))
        
        # Throughput reflects vehicles processed
        fixed_throughput = int(step * 2.8)
        adaptive_throughput = int(step * 3.7) # ~32% gain
        
        data.append({
            "simulation_step": step,
            "fixed_avg_wait_sec": round(fixed_wait, 1),
            "adaptive_avg_wait_sec": round(adaptive_wait, 1),
            "fixed_throughput_veh": fixed_throughput,
            "adaptive_throughput_veh": adaptive_throughput
        })
    return data

# --- REPORT DOWNLOAD ENDPOINTS ---

@app.get("/api/reports/download/csv")
def download_csv_report(type: str = "violations", db: Session = Depends(get_db)):
    """Exports structured database logs (violations or metrics) as a CSV file."""
    output = StringIO()
    writer = csv.writer(output)
    
    if type == "violations":
        writer.writerow(["ID", "Junction Name", "Lane Location", "Timestamp", "Violation Type", "Vehicle Type"])
        violations = db.query(Violation).order_by(Violation.timestamp.desc()).all()
        for v in violations:
            lane = db.query(Lane).filter(Lane.id == v.lane_id).first()
            j_name = db.query(Junction).filter(Junction.id == lane.junction_id).first().name if lane else "Unknown"
            writer.writerow([v.id, j_name, lane.lane_name if lane else "", v.timestamp.strftime('%Y-%m-%d %H:%M:%S'), v.violation_type, v.vehicle_type])
            
        filename = f"erakshak_violations_{datetime.datetime.now().strftime('%d-%m-%Y')}.csv"
    else:
        writer.writerow(["ID", "Lane ID", "Timestamp", "Vehicle Count", "Queue Length (m)", "Occupancy Ratio", "Avg Speed (km/h)"])
        metrics = db.query(TrafficMetric).order_by(TrafficMetric.timestamp.desc()).limit(100).all()
        for m in metrics:
            writer.writerow([m.id, m.lane_id, m.timestamp.strftime('%Y-%m-%d %H:%M:%S'), m.vehicle_count, m.queue_length_m, m.occupancy_ratio, m.average_speed_kmh])
            
        filename = f"erakshak_metrics_{datetime.datetime.now().strftime('%d-%m-%Y')}.csv"

    output.seek(0)
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(output, media_type="text/csv", headers=headers)

@app.get("/api/reports/download/pdf")
def download_pdf_report(db: Session = Depends(get_db)):
    """Generates and downloads a print-ready command center analytical PDF report."""
    pdf_stream = generate_pdf_report(db)
    filename = f"erakshak_traffic_report_{datetime.datetime.now().strftime('%d-%m-%Y_%H%M')}.pdf"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(pdf_stream, media_type="application/pdf", headers=headers)

# --- WEBSOCKET ENGINE ---

@app.websocket("/api/ws/traffic")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint establishing low-latency state stream to React clients.
    Broadcasts live camera measurements, signal adjustments, intrusions, and recommendation alerts.
    """
    await websocket.accept()
    print("WebSocket: Client connected.")
    
    # Create an async queue for this client connection and register with the event bus
    client_queue = asyncio.Queue()
    event_bus.register_queue(client_queue)
    
    # 1. Send the initial system state to the client immediately upon connection.
    # Prevents blank screen states before the next mock timer loop runs.
    db = SessionLocal()
    try:
        junctions = db.query(Junction).all()
        for j in junctions:
            total_v = 0
            total_q = 0.0
            lanes_data = []
            
            for lane in j.lanes:
                latest = db.query(TrafficMetric).filter(
                    TrafficMetric.lane_id == lane.id
                ).order_by(TrafficMetric.timestamp.desc()).first()
                
                v_count = latest.vehicle_count if latest else 0
                q_len = latest.queue_length_m if latest else 0.0
                occ = latest.occupancy_ratio if latest else 0.0
                spd = latest.average_speed_kmh if latest else 40.0
                
                total_v += v_count
                total_q += q_len
                
                lanes_data.append({
                    "lane_id": lane.id,
                    "lane_name": lane.lane_name,
                    "direction": lane.direction,
                    "is_brts": lane.is_brts,
                    "polygon_coords": lane.polygon_coords,
                    "vehicle_count": v_count,
                    "queue_length_m": q_len,
                    "occupancy_ratio": occ,
                    "average_speed_kmh": spd
                })
            
            avg_q = total_q / len(j.lanes) if j.lanes else 0.0
            
            # Count recent intrusions
            ten_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
            intrusion_count = db.query(Violation).join(Lane).filter(
                Lane.junction_id == j.id,
                Violation.violation_type == "brts_intrusion",
                Violation.timestamp >= ten_mins_ago
            ).count()
            
            # Active recommendations
            active_recs = db.query(Recommendation).filter(
                Recommendation.junction_id == j.id,
                Recommendation.status == "pending"
            ).all()

            await websocket.send_json({
                "type": "junction_update",
                "junction_id": j.id,
                "name": j.name,
                "latitude": j.latitude,
                "longitude": j.longitude,
                "signal_mode": j.signal_mode,
                "current_phase": j.current_phase,
                "cycle_length": j.cycle_length,
                "total_vehicles": total_v,
                "avg_queue_length_m": round(avg_q, 1),
                "brts_intrusion_count": intrusion_count,
                "active_recommendations_count": len(active_recs),
                "lanes": lanes_data
            })
    except Exception as e:
        print(f"WebSocket: Error sending initial state: {e}")
    finally:
        db.close()

    # 2. Maintain active pipeline: block and wait for events published to event_bus,
    # then push them directly to this websocket client.
    try:
        while True:
            event = await client_queue.get()
            # event structure is {"channel": channel, "data": dict}
            await websocket.send_json(event["data"])
    except Exception as e:
        print(f"WebSocket: Client connection closed ({e}).")
    finally:
        event_bus.unregister_queue(client_queue)
