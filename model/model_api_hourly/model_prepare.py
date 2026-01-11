import psycopg2
import pandas as pd
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python.config import DB_CONFIG

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    # รวมข้อมูลจากทั้งสองตาราง: air4thai_hourly (real-time) และ pm25_daily_avg (historical)
    query = """
        SELECT 
            h.station_id, 
            h.timestamp::date as date,  -- แปลงเป็น date
            AVG(h.pm25) as pm25_avg,   -- ค่าเฉลี่ยรายวันจาก hourly
            h.area
        FROM air4thai_hourly h
        WHERE h.pm25 IS NOT NULL
        GROUP BY h.station_id, h.timestamp::date, h.area
        UNION ALL
        SELECT 
            NULL as station_id,  -- historical ไม่มี station_id
            d.date,
            d.pm25_avg,
            NULL as area
        FROM pm25_daily_avg d
        ORDER BY date;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

#สร้าง feature engineering --> lag() function
def create_features(df):
    df = df.sort_values("timestamp")        #time-series ต้องเรียงตามเวลา --> ต้อง sort
    df = df.set_index("timestamp")          #setting timestamp เป็น index ทำให้สร้าง lag/rolling ง่ายขึ้น

    for lag in (1,3,6,12,24):       #หน่วย hour
        df[f"pm25_lag_{lag}"] = df["pm25"].shift(lag)

    df["pm25_roll_3"] = df["pm25"].rolling(3).mean()
    df["pm25_roll_12"] = df["pm25"].rolling(12).mean()
    df["pm25_roll_24"] = df["pm25"].rolling(24).mean()

    df["hour"] = df.index.hour              #pollution มักขึ้นสูงตอนเช้า/เย็น --> hour สำคัญมาก
    df["dayofweek"] = df.index.dayofweek    #วันธรรมดา (no sat, sun)
    df["month"] = df.index.month

    df = df.dropna()
    
    return df


def prepare_dataset():
    df = load_data()
    df_feat = create_features(df)

    df_feat["target_pm25"] = df_feat["pm25"].shift(-1)

    df_feat = df_feat.dropna()

    output_path = os.path.join(os.path.dirname(__file__), "dataset_pm25.csv")
    df_feat.to_csv(output_path, index=False)

    print(f"Dataset saved -> {output_path}")

if __name__ == "__main__":
    prepare_dataset()




