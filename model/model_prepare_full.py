import psycopg2
import pandas as pd
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python.config import DB_CONFIG

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    # ใช้ข้อมูล 15 ปีจาก pm25_daily_bangkok
    query = """
        SELECT
            date as timestamp,
            pm25
        FROM pm25_daily_bangkok
        WHERE pm25 IS NOT NULL
        ORDER BY date;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

#สร้าง feature engineering สำหรับข้อมูล daily
def create_features(df):
    df = df.sort_values("timestamp")
    df = df.set_index("timestamp")
    df.index = pd.to_datetime(df.index)

    # Lag features (หน่วยวัน)
    for lag in [1, 3, 7, 14, 30]:
        df[f"pm25_lag_{lag}"] = df["pm25"].shift(lag)

    # Rolling means
    for window in [7, 14, 30]:
        df[f"pm25_roll_{window}"] = df["pm25"].rolling(window).mean()

    # Time features
    df["dayofweek"] = df.index.dayofweek
    df["month"] = df.index.month
    df["year"] = df.index.year

    # Seasonal features
    df["quarter"] = df.index.quarter
    df["is_weekend"] = df.index.dayofweek >= 5

    df = df.dropna()

    return df

def prepare_dataset():
    df = load_data()
    df_feat = create_features(df)

    # Target: pm25 ของวันถัดไป
    df_feat["target_pm25"] = df_feat["pm25"].shift(-1)
    df_feat = df_feat.dropna()

    # เลือก features และ target
    feature_cols = [col for col in df_feat.columns if col not in ["pm25", "target_pm25"]]
    X = df_feat[feature_cols]
    y = df_feat["target_pm25"]

    # บันทึก dataset
    output_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(output_dir, "dataset_pm25_full.csv")
    df_feat.to_csv(dataset_path, index=True)
    print(f"Dataset saved to {dataset_path}")

    return X, y

if __name__ == "__main__":
    prepare_dataset()