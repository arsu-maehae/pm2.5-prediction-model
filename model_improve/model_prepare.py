import psycopg2
import pandas as pd
from python.config import DB_CONFIG
import os

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT station_id, timestamp, pm25, pm10, o3, no2, co, so2
        FROM air4thai_hourly
        WHERE pm25 IS NOT NULL
        ORDER BY timestamp;
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

    # add rolling features
    df['pm25_roll_min_6'] = df['pm25'].rolling(6).min()
    df['pm25_roll_max_6'] = df['pm25'].rolling(6).max()
    df['pm25_roll_std_12'] = df['pm25'].rolling(12).std()
    df['pm25_roll_std_24'] = df['pm25'].rolling(24).std()

    df["hour"] = df.index.hour              #pollution มักขึ้นสูงตอนเช้า/เย็น --> hour สำคัญมาก
    df["dayofweek"] = df.index.dayofweek    #วันธรรมดา (no sat, sun)
    df["month"] = df.index.month

    # add
    df["is_weekend"] = (df.index.dayofweek >= 5).astype(int)

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




