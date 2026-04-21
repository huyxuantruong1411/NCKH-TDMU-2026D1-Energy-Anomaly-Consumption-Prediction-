import json
import threading
import traceback
from kafka import KafkaConsumer
from app.database import SessionLocal, EnergyRecord
from app.ai_core import detector

def consume_messages():
    try:
        consumer = KafkaConsumer(
            "energy_stream",
            bootstrap_servers=['localhost:29092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='energy_enterprise_group'
        )
        print("✅ Consumer Enterprise đang chạy...")
        
        for message in consumer:
            db = SessionLocal()
            try:
                data = message.value
                ts, b_name, actual, feats = data["timestamp"], data["building_name"], data["actual_load"], data["features"]
                
                predicted, anomaly_flag, threshold, temp, dew, wind, pressure, explanation = detector.predict_and_detect(b_name, actual, feats)
                
                record = EnergyRecord(
                    timestamp=ts, building_name=b_name, actual_load=actual,
                    predicted_load=predicted, threshold=threshold, is_anomaly=anomaly_flag,
                    weather_temp=temp, weather_dew=dew, weather_wind=wind, weather_pressure=pressure, ai_explanation=explanation
                )
                db.add(record)
                db.commit()
            except Exception as inner_e:
                db.rollback()
                print(f"Lỗi xử lý message: {inner_e}")
            finally:
                db.close()
    except Exception as e:
        print(f"❌ Lỗi khởi tạo Consumer: {e}")

def start_consumer_thread():
    threading.Thread(target=consume_messages, daemon=True).start()