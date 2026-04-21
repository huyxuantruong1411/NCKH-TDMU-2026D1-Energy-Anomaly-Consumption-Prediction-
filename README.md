# ⚡ Enterprise Energy Anomaly Detection System (EEADS)

An enterprise-grade, real-time energy anomaly detection and management system. Powered by a **Big Data Pipeline** and **Explainable AI (XAI)**, EEADS provides deep analytics, anomaly forecasting, and actionable insights for up to 50 buildings simultaneously.

## 🌟 Introduction
EEADS is designed for Energy Portfolio Managers to monitor real-time electricity loads. By combining **XGBoost** with a dynamic **Rolling IQR** threshold algorithm, the system accurately flags anomalous consumption spikes. More importantly, it features an **Explainable AI (XAI)** module that translates complex machine learning features into human-readable technical advice, enabling rapid decision-making.

## ✨ Key Features
* **Real-time Streaming:** Continuous data processing pipeline using Apache Kafka.
* **AI Forecasting & Anomaly Detection:** XGBoost model optimized via Optuna, paired with dynamic thresholding to minimize false positives.
* **Explainable AI (XAI):** Automatically diagnoses the root causes of anomalies (e.g., Thermal Lag, Rapid Load Shifts, Weather impact) and provides actionable maintenance advice.
* **Deep Environment Analytics:** Multi-variate correlation analysis combining energy loads with micro-climate data (Temperature, Dew Point, Wind Speed, Pressure).
* **Hourly Load Profiling:** Generates historical baselines to identify peak hours and optimize maintenance schedules.
* **Global Alert Center:** Real-time notification bell with cross-building shortcut navigation and historical snapshot modals.
* **Fault Injection Simulator:** Built-in capability to inject artificial anomalies (configurable probability and multiplier) for demonstration and testing purposes.

## 🏗️ System Architecture
1. **Simulator (Producer):** Ingests and merges load and weather data from the "Building Data Genome 2" dataset, simulating a real-time IoT sensor network.
2. **Message Broker:** Apache Kafka buffers and distributes the high-throughput data stream.
3. **Backend (Consumer & API):** FastAPI serves as the core logic engine, executing the AI model, performing XAI translations, and providing RESTful endpoints.
4. **Database:** PostgreSQL stores operational history, weather data, and AI evaluation logs.
5. **Frontend (Enterprise SPA):** A highly responsive Single Page Application built with Vanilla JS, HTML5 Grid, and Chart.js, featuring zero-latency updates and deep-scroll analytics.

## 🚀 Installation & Setup

### 1. Prerequisites
* Python 3.9+
* Docker & Docker Compose (for Kafka)
* PostgreSQL 13+ (Local instance running on port 5432)

### 2. Environment Setup
Clone the repository and install dependencies:
```bash
git clone [https://github.com/huyxuantruong1411/NCKH-TDMU-2026D1-Energy-Anomaly-Consumption-Prediction-.git](https://github.com/huyxuantruong1411/NCKH-TDMU-2026D1-Energy-Anomaly-Consumption-Prediction-.git)
cd energy-anomaly-project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows: venv\Scripts\activate
# On Linux/Mac: source venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt
```

### 3. Infrastructure Initialization
```bash
# Start Apache Kafka via Docker
docker-compose up -d

# Initialize Database and clear old Kafka topics
python reset_system.py
```

### 4. Running the System
You need to open **3 separate Terminals** (ensure the virtual environment is activated in each):

* **Terminal 1 (Backend API):**
  ```bash
  cd backend
  uvicorn app.main:app --reload --port 8000
  ```
* **Terminal 2 (Frontend UI Server):**
  ```bash
  python run_ui.py
  ```
* **Terminal 3 (Data Simulator):**
  ```bash
  cd simulator
  python producer.py
  ```

Once all services are running, open your browser and navigate to: **`http://localhost:8050`**

## 📊 Dataset Reference
This project utilizes the [Building Data Genome Project 2](https://github.com/buds-lab/building-data-genome-project-2) dataset, combining hourly electricity meter readings with localized weather station data.

## 🛠️ Technology Stack
* **Language:** Python, JavaScript (ES6)
* **Machine Learning:** XGBoost, Scikit-learn, Pandas, Numpy
* **Data Pipeline:** Apache Kafka (`confluent-kafka`)
* **Backend:** FastAPI, SQLAlchemy
* **Database:** PostgreSQL
* **Frontend:** Chart.js, HTML5/CSS3 (CSS Grid/Flexbox)

---
---

# ⚡ Hệ thống Quản lý và Phát hiện Bất thường Năng lượng (EEADS)

Hệ thống phát hiện bất thường và quản lý năng lượng thời gian thực cấp doanh nghiệp. Được vận hành bởi **Big Data Pipeline** và **Trí tuệ Nhân tạo Giải thích được (XAI)**, EEADS cung cấp các phân tích chuyên sâu, dự báo sự cố và tự động đưa ra lời khuyên hành động cho mạng lưới lên đến 50 tòa nhà cùng lúc.

## 🌟 Giới thiệu
EEADS được thiết kế dành riêng cho các Giám đốc Quản lý Năng lượng. Bằng cách kết hợp mô hình **XGBoost** với thuật toán ngưỡng động **Rolling IQR**, hệ thống phát hiện chính xác các cú sốc tải tiêu thụ. Điểm đột phá nằm ở module **Hệ chuyên gia XAI**, có khả năng phiên dịch các độ đo học máy phức tạp thành ngôn ngữ nghiệp vụ dễ hiểu, giúp đội ngũ kỹ thuật đưa ra quyết định bảo trì nhanh chóng.

## ✨ Tính năng nổi bật
* **Truyền phát Thời gian thực (Real-time Streaming):** Xử lý luồng dữ liệu IoT liên tục thông qua Apache Kafka.
* **Dự báo & Phát hiện Bất thường:** Mô hình XGBoost tối ưu hóa bằng Optuna, kết hợp với dải an toàn (Threshold Band) động để giảm thiểu báo động giả.
* **Trí tuệ Nhân tạo Giải thích được (XAI):** Tự động chẩn đoán nguyên nhân gốc rễ (Sốc tải đột ngột, Trễ nhiệt, Khí hậu cực đoan...) và đề xuất biện pháp xử lý cụ thể.
* **Phân tích Vi khí hậu Chuyên sâu:** Tương quan đa biến giữa tiêu thụ điện và các chỉ số môi trường (Nhiệt độ, Độ ẩm sương, Tốc độ gió, Áp suất).
* **Hồ sơ Phụ tải (Hourly Profile):** Xây dựng biểu đồ hành vi tiêu thụ lịch sử để xác định giờ cao điểm và tối ưu hóa lịch bảo trì.
* **Trung tâm Thông báo Toàn cục:** Quả chuông cảnh báo thời gian thực, hỗ trợ chuyển hướng (shortcut) nhanh giữa các tòa nhà và lưu trữ Camera trạng thái (Snapshot) của từng sự cố.
* **Mô phỏng Tiêm Lỗi (Fault Injection):** Tích hợp sẵn cơ chế tiêm lỗi nhân tạo tự động vào luồng dữ liệu để phục vụ mục đích kiểm thử và Demo.

## 🏗️ Kiến trúc hệ thống
1. **Simulator (Producer):** Mô phỏng trạm thu thập dữ liệu điện năng và thời tiết từ bộ dataset "Building Data Genome 2".
2. **Message Broker:** Apache Kafka làm bộ đệm trung chuyển, chịu tải và phân phối dữ liệu tốc độ cao.
3. **Backend (Consumer & API):** FastAPI đóng vai trò lõi logic, chạy AI, tính toán XAI và cung cấp RESTful API.
4. **Database:** PostgreSQL lưu trữ dữ liệu vận hành, vi khí hậu và nhật ký đánh giá của AI.
5. **Frontend (Enterprise SPA):** Giao diện Single Page Application xây dựng bằng Vanilla JS, CSS Grid và Chart.js, đảm bảo tốc độ phản hồi zero-latency.

## 🚀 Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
* Python 3.9+
* Docker & Docker Compose (để chạy Kafka)
* PostgreSQL 13+ (Chạy local ở port 5432)

### 2. Cài đặt Môi trường
Clone dự án và cài đặt các thư viện cần thiết:
```bash
git clone [https://github.com/huyxuantruong1411/NCKH-TDMU-2026D1-Energy-Anomaly-Consumption-Prediction-.git](https://github.com/huyxuantruong1411/NCKH-TDMU-2026D1-Energy-Anomaly-Consumption-Prediction-.git)
cd energy-anomaly-project

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows: venv\Scripts\activate
# Trên Linux/Mac: source venv/bin/activate

# Cài đặt thư viện
pip install -r backend/requirements.txt
```

### 3. Khởi tạo Hạ tầng
```bash
# Khởi động Apache Kafka qua Docker
docker-compose up -d

# Khởi tạo CSDL và làm sạch Kafka topics cũ
python reset_system.py
```

### 4. Chạy Hệ thống
Bạn cần mở **3 Terminal độc lập** (đảm bảo đã kích hoạt môi trường ảo `venv` ở cả 3):

* **Terminal 1 (Backend API):**
  ```bash
  cd backend
  uvicorn app.main:app --reload --port 8000
  ```
* **Terminal 2 (Giao diện Web Server):**
  ```bash
  python run_ui.py
  ```
* **Terminal 3 (Simulator Bơm dữ liệu):**
  ```bash
  cd simulator
  python producer.py
  ```

Khi các dịch vụ đã báo chạy thành công, mở trình duyệt web và truy cập: **`http://localhost:8050`**

## 📊 Dataset Tham chiếu
Dự án sử dụng bộ dữ liệu [Building Data Genome Project 2](https://github.com/buds-lab/building-data-genome-project-2), kết hợp giữa dữ liệu công tơ điện hàng giờ và trạm thời tiết khu vực.

## 🛠️ Công nghệ sử dụng
* **Ngôn ngữ:** Python, JavaScript (ES6)
* **AI/ML:** XGBoost, Scikit-learn, Pandas, Numpy
* **Data Pipeline:** Apache Kafka (`confluent-kafka`)
* **Backend:** FastAPI, SQLAlchemy
* **Database:** PostgreSQL
* **Frontend:** Chart.js, HTML5/CSS3 (CSS Grid/Flexbox)