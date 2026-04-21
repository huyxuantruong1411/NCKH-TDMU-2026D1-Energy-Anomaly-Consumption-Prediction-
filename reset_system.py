import time
from sqlalchemy import create_engine, text
from kafka.admin import KafkaAdminClient
from kafka.errors import UnknownTopicOrPartitionError

DATABASE_URL = "postgresql://postgres:14112002@localhost:5432/energy_db"
KAFKA_BROKER = "localhost:29092"
TOPIC_NAME = "energy_stream"

def reset_database():
    print(f"🔄 Đang kết nối Database: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS energy_records CASCADE;"))
        print("✅ [Database] Đã xóa hoàn toàn bảng cũ. Bảng mới (có XAI và Weather) sẽ được tạo tự động.")
    except Exception as e:
        print(f"❌ [Database] Lỗi khi dọn dẹp DB: {e}")

def reset_kafka():
    print(f"🔄 Đang kết nối Kafka: {KAFKA_BROKER}")
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER)
        admin_client.delete_topics([TOPIC_NAME])
        print(f"✅ [Kafka] Đã xóa Topic '{TOPIC_NAME}'.")
        time.sleep(2) 
    except UnknownTopicOrPartitionError:
        print(f"⚠️ [Kafka] Topic không tồn tại.")
    except Exception as e:
        print(f"❌ [Kafka] Lỗi Kafka: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🚧 BẮT ĐẦU RESET HỆ THỐNG (ENTERPRISE UPGRADE) 🚧")
    reset_database()
    reset_kafka()
    print("🎉 HOÀN TẤT RESET!")