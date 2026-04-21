import http.server
import socketserver
import os

PORT = 8050
DIRECTORY = "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

# Chuyển hướng server vào thư mục frontend
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("="*60)
    print(f"🚀 GIAO DIỆN WEB ĐÃ KHỞI ĐỘNG THÀNH CÔNG!")
    print(f"👉 Hãy mở trình duyệt và truy cập: http://localhost:{PORT}")
    print("="*60)
    print("Nhấn Ctrl+C để tắt Web Server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã tắt Web Server.")