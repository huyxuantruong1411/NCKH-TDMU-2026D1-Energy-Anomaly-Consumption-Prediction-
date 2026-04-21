import pandas as pd
import numpy as np
import json
import time
import random # Dùng để tiêm lỗi ngẫu nhiên
from kafka import KafkaProducer
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def json_serializer(data): return json.dumps(data).encode("utf-8")
producer = KafkaProducer(bootstrap_servers=['localhost:29092'], value_serializer=json_serializer)

print("Đang nạp dữ liệu Thời tiết toàn cầu vào RAM...")
global_weather_df = pd.read_csv("data/weather.csv", parse_dates=['timestamp'])

def load_and_merge_data(b_name, df_weather):
    df_elec = pd.read_csv("data/electricity_cleaned.csv", usecols=['timestamp', b_name], parse_dates=['timestamp'])
    df_elec = df_elec.set_index('timestamp').interpolate(method='linear', limit_direction='both').fillna(0)
    site_id = b_name.split('_')[0] 
    weather_site = df_weather[df_weather['site_id'] == site_id].copy().set_index('timestamp')
    target_weather_cols = ['airTemperature', 'dewTemperature', 'windSpeed', 'cloudCoverage', 'precipDepth1HR']
    available_weather = [c for c in target_weather_cols if c in weather_site.columns]
    weather_numeric = weather_site[available_weather].resample('h').mean().interpolate(method='linear', limit_direction='both').bfill().ffill()
    temp_df = pd.DataFrame(df_elec[b_name]).rename(columns={b_name: 'load'})
    df_final = temp_df.merge(weather_numeric, left_index=True, right_index=True, how='left').reset_index()
    df_final['building_name'] = b_name
    le = LabelEncoder()
    df_final['building_id'] = le.fit_transform(df_final['building_name'])
    df_final['log_load'] = np.log1p(df_final['load'])
    return df_final

def create_advanced_features(df):
    df = df.sort_values(['building_id', 'timestamp'])
    grouped = df.groupby('building_id')
    df['hour'] = df.timestamp.dt.hour.astype(np.int8)
    df['dayofweek'] = df.timestamp.dt.dayofweek.astype(np.int8)
    df['month'] = df.timestamp.dt.month.astype(np.int8)
    df['is_weekend'] = (df['dayofweek'] >= 5).astype(np.int8)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24).astype(np.float32)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24).astype(np.float32)
    for lag in [1, 2, 3, 4, 5, 6, 24, 48, 168]: df[f'load_lag_{lag}'] = grouped['log_load'].shift(lag).astype(np.float32)
    df['roll_mean_3h'] = grouped['log_load'].transform(lambda x: x.rolling(3).mean()).astype(np.float32)
    df['roll_std_3h'] = grouped['log_load'].transform(lambda x: x.rolling(3).std()).astype(np.float32)
    df['roll_mean_24h'] = grouped['log_load'].transform(lambda x: x.rolling(24).mean()).astype(np.float32)
    df['roll_max_24h'] = grouped['log_load'].transform(lambda x: x.rolling(24).max()).astype(np.float32)
    df['roll_min_24h'] = grouped['log_load'].transform(lambda x: x.rolling(24).min()).astype(np.float32)
    df['load_ratio_24h'] = (df['load_lag_1'] / (df['roll_mean_24h'] + 1e-5)).astype(np.float32)
    if 'airTemperature' in df.columns:
        for i in range(1, 7): df[f'temp_lag_{i}'] = df.groupby('building_id')['airTemperature'].shift(i).astype(np.float32)
        df['temp_roll_mean_6h'] = grouped['airTemperature'].transform(lambda x: x.rolling(6).mean()).astype(np.float32)
        df['temp_roll_std_6h'] = grouped['airTemperature'].transform(lambda x: x.rolling(6).std()).astype(np.float32)
    for d in [1, 2, 3, 4, 5, 6, 24]: df[f'load_diff_{d}'] = grouped['log_load'].diff(d).astype(np.float32)
    if 'dewTemperature' in df.columns and 'airTemperature' in df.columns:
        df['enthalpy'] = (1.006 * df['airTemperature'] + 0.622 * df['dewTemperature']).astype(np.float32)
    return df.dropna()

if __name__ == "__main__":
    df_headers = pd.read_csv("data/electricity_cleaned.csv", nrows=0)
    valid_columns = [col for col in df_headers.columns if col.lower() != 'timestamp' and not col.startswith('Unnamed')]
    target_buildings = valid_columns[:50]
    print(f"✅ Tự động chọn {len(target_buildings)} tòa nhà.")
    
    all_data = []
    for idx, b in enumerate(target_buildings):
        print(f"[{idx+1}/{len(target_buildings)}] Nạp dữ liệu: {b}...")
        df_raw = load_and_merge_data(b, global_weather_df)
        all_data.append(create_advanced_features(df_raw).iloc[500:])
        
    df_stream = pd.concat(all_data).sort_values('timestamp')
    feature_cols = [c for c in df_stream.columns if c not in ['timestamp', 'load', 'log_load', 'building_name']]
    
    # --- CẤU HÌNH TIÊM LỖI DEMO ---
    INJECT_FAULT_RATE = 0.02 # Tỉ lệ 2% bị dính lỗi để Demo (Trung bình 1 tiếng có 1 tòa dính chưởng)
    FAULT_MULTIPLIER = 1.8 # Nhân tải thực tế lên 1.8 lần (Gây đột biến)
    
    print("="*60)
    print(f"🚀 BẮT ĐẦU STREAM + CHẾ ĐỘ TIÊM LỖI TỰ ĐỘNG ({INJECT_FAULT_RATE*100}%)")
    print("="*60)
    
    grouped = df_stream.groupby('timestamp')
    for ts, group in grouped:
        print(f"--- Mạng lưới khung giờ: {ts} ---")
        for _, row in group.iterrows():
            features_array = row[feature_cols].tolist()
            actual_load = float(row["load"])
            
            # [TIÊM LỖI]: Bắt xác suất ngẫu nhiên
            is_injected = False
            if random.random() < INJECT_FAULT_RATE:
                actual_load = actual_load * FAULT_MULTIPLIER # Tăng vọt tải
                is_injected = True
                
            payload = {
                "timestamp": str(ts), 
                "building_name": row["building_name"],
                "actual_load": actual_load, 
                "features": features_array
            }
            producer.send("energy_stream", payload)
            
            if is_injected:
                print(f"💥 [INJECTED FAULT] Đã tiêm lỗi vào {row['building_name']} (Load: {actual_load:.2f})")
            
        time.sleep(0.5)