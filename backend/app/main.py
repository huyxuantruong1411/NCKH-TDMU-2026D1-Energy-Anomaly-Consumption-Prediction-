from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal, EnergyRecord
from app.kafka_consumer import start_consumer_thread
import json
from collections import defaultdict

app = FastAPI(title="Energy Enterprise API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    start_consumer_thread()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/api/buildings")
def get_buildings(db: Session = Depends(get_db)):
    buildings = db.query(EnergyRecord.building_name).distinct().all()
    return [b[0] for b in buildings]

@app.get("/api/data")
def get_latest_data(building_name: str, limit: int = 150, db: Session = Depends(get_db)):
    records = db.query(EnergyRecord).filter(EnergyRecord.building_name == building_name).order_by(EnergyRecord.id.desc()).limit(limit).all()
    return list(reversed(records))

@app.get("/api/stats/summary")
def get_daily_summary(building_name: str, db: Session = Depends(get_db)):
    subq = db.query(EnergyRecord.actual_load.label('load')).filter(EnergyRecord.building_name == building_name).order_by(EnergyRecord.id.desc()).limit(24).subquery()
    stats = db.query(func.sum(subq.c.load), func.max(subq.c.load), func.min(subq.c.load)).first()
    return {"sum": stats[0] or 0, "max": stats[1] or 0, "min": stats[2] or 0}

@app.get("/api/weather/correlation")
def get_weather_correlation(building_name: str, limit: int = 168, db: Session = Depends(get_db)):
    records = db.query(EnergyRecord).filter(EnergyRecord.building_name == building_name).order_by(EnergyRecord.id.desc()).limit(limit).all()
    return [{
        "time": r.timestamp.split(" ")[1], 
        "temp": r.weather_temp or 0, "dew": r.weather_dew or 0, 
        "wind": r.weather_wind or 0, "pressure": r.weather_pressure or 0, 
        "load": r.actual_load
    } for r in reversed(records)]

@app.get("/api/explain")
def get_explanation(building_name: str, db: Session = Depends(get_db)):
    record = db.query(EnergyRecord).filter(EnergyRecord.building_name == building_name, EnergyRecord.is_anomaly == 1).order_by(EnergyRecord.id.desc()).first()
    if record and record.ai_explanation:
        return {"timestamp": record.timestamp, "load": record.actual_load, "explanation": json.loads(record.ai_explanation)}
    return {"status": "No recent anomaly"}

@app.get("/api/alerts/global")
def get_global_alerts(db: Session = Depends(get_db)):
    alerts = db.query(EnergyRecord.timestamp, EnergyRecord.building_name, EnergyRecord.actual_load)\
               .filter(EnergyRecord.is_anomaly == 1).order_by(EnergyRecord.id.desc()).limit(10).all()
    return [{"timestamp": r[0], "building": r[1], "load": r[2]} for r in alerts]

# [API LỊCH SỬ SỰ CỐ TÒA NHÀ] - Dành cho tính năng Snapshot Modal
@app.get("/api/alerts/history")
def get_building_alerts_history(building_name: str, db: Session = Depends(get_db)):
    alerts = db.query(EnergyRecord).filter(EnergyRecord.building_name == building_name, EnergyRecord.is_anomaly == 1).order_by(EnergyRecord.id.desc()).limit(50).all()
    result = []
    for r in alerts:
        result.append({
            "timestamp": r.timestamp,
            "actual_load": r.actual_load,
            "predicted_load": r.predicted_load,
            "temp": r.weather_temp, "dew": r.weather_dew, "wind": r.weather_wind,
            "explanation": json.loads(r.ai_explanation) if r.ai_explanation else {}
        })
    return result

@app.get("/api/analytics/hourly_profile")
def get_hourly_profile(building_name: str, db: Session = Depends(get_db)):
    records = db.query(EnergyRecord.timestamp, EnergyRecord.actual_load).filter(EnergyRecord.building_name == building_name).order_by(EnergyRecord.id.desc()).limit(1000).all()
    hourly_loads = defaultdict(list)
    for r in records:
        hour = r[0].split(" ")[1].split(":")[0] 
        hourly_loads[hour].append(r[1])
    profile = []
    for h in sorted(hourly_loads.keys()):
        profile.append({"hour": f"{h}:00", "avg_load": sum(hourly_loads[h]) / len(hourly_loads[h])})
    return profile