from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Đã đổi port sang 5433
DATABASE_URL = "postgresql://postgres:14112002@localhost:5433/energy_db"

def test_connection():
    print(f"Đang thử kết nối đến: {DATABASE_URL} ...\n")
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            print("✅ KẾT NỐI THÀNH CÔNG!")
            print("Database 'energy_db' trong Docker đang hoạt động và sẵn sàng nhận dữ liệu.")
            
    except OperationalError as e:
        print("❌ KẾT NỐI THẤT BẠI!")
        print("Vui lòng kiểm tra lại:")
        print(" 1. Docker đã chạy lệnh 'docker-compose up -d' chưa?")
        print(" 2. Container 'energy_postgres' có đang ở trạng thái 'Up' không?")
        print(f"\nChi tiết lỗi từ hệ thống:\n{e}")
    except Exception as e:
        print("❌ Đã xảy ra lỗi không xác định:")
        print(e)

if __name__ == "__main__":
    test_connection()