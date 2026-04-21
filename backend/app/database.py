from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:14112002@localhost:5432/energy_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EnergyRecord(Base):
    __tablename__ = "energy_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, index=True)
    building_name = Column(String, index=True)
    actual_load = Column(Float)
    predicted_load = Column(Float)
    threshold = Column(Float)
    is_anomaly = Column(Integer)
    # [MỞ RỘNG THỜI TIẾT ĐỂ PHÂN TÍCH]
    weather_temp = Column(Float, nullable=True)
    weather_dew = Column(Float, nullable=True)
    weather_wind = Column(Float, nullable=True) # Tốc độ gió
    weather_pressure = Column(Float, nullable=True) # Áp suất
    ai_explanation = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)