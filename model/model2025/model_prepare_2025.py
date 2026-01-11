import psycopg2
import pandas as pd
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python.config import DB_CONFIG

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    # ใช้ข้อมูลจาก pm25_bangkok_2025 (ปี 2025 เฉพาะกรุงเทพฯ)
    query = """
        SELECT 
            station_id, 
            date as timestamp,  -- เปลี่ยนชื่อเป็น timestamp
            pm25
        FROM pm25_bangkok_2025
        WHERE pm25 IS NOT NULL
        ORDER BY date;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

#สร้าง feature engineering --> lag() function สำหรับข้อมูล daily
def create_features(df):
    df = df.sort_values("timestamp")        #time-series ต้องเรียงตามเวลา
    df = df.set_index("timestamp")          #setting timestamp เป็น index ทำให้สร้าง lag/rolling ง่ายขึ้น
    df.index = pd.to_datetime(df.index)     # แปลงเป็น datetime

    for lag in (1,3,6,12,24):       #หน่วยวัน (ไม่ใช่ชั่วโมง)
        df[f"pm25_lag_{lag}"] = df["pm25"].shift(lag)

    df["pm25_roll_3"] = df["pm25"].rolling(3).mean()
    df["pm25_roll_12"] = df["pm25"].rolling(12).mean()
    df["pm25_roll_24"] = df["pm25"].rolling(24).mean()

    df["dayofweek"] = df.index.dayofweek    #วันในสัปดาห์
    df["month"] = df.index.month

    df = df.dropna()
    
    return df


def prepare_dataset():
    df = load_data()
    df_feat = create_features(df)

    df_feat["target_pm25"] = df_feat["pm25"].shift(-1)  # ทำนาย 1 วันถัดไป

    df_feat = df_feat.dropna()

    output_path = os.path.join(os.path.dirname(__file__), "dataset_pm25_2025.csv")
    df_feat.to_csv(output_path, index=False)

    print(f"Dataset saved -> {output_path}")