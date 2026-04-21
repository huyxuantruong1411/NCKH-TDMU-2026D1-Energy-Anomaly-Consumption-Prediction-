from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Chuỗi kết nối của bạn
DATABASE_URL = "postgresql://postgres:14112002@localhost:5432/energy_db"

def test_connection():
    print(f"Đang thử kết nối đến: {DATABASE_URL} ...\n")
    try:
        # Khởi tạo engine
        engine = create_engine(DATABASE_URL)
        
        # Thử mở một kết nối
        with engine.connect() as connection:
            print("✅ KẾT NỐI THÀNH CÔNG!")
            print("Database 'energy_db' đang hoạt động và sẵn sàng nhận dữ liệu.")
            
    except OperationalError as e:
        print("❌ KẾT NỐI THẤT BẠI!")
        print("Vui lòng kiểm tra lại:")
        print(" 1. PostgreSQL đã được bật trên máy chưa?")
        print(" 2. Mật khẩu '1411' hoặc user 'postgres' có chính xác không?")
        print(" 3. Database 'energy_db' đã được tạo chưa?")
        print(f"\nChi tiết lỗi từ hệ thống:\n{e}")
    except Exception as e:
        print("❌ Đã xảy ra lỗi không xác định:")
        print(e)

if __name__ == "__main__":
    test_connection()