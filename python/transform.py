# ทำความสะอาดข้อมูลจาก Air4Thai ให้อยู่ในรูปแบบที่ต้องการ

import pandas as pd

def clean_air_data(df):
    print("Columns from fetch:", df.columns.tolist())

    # mapping คอลัมน์ซับซ้อนของ Air4Thai → ฟิลด์มาตรฐาน
    rename_map = {
        "stationID": "station_id",
        "nameTH": "station_name",
        "nameEN": "station_name_en",
        "areaTH": "area",
        "AQILast.time": "timestamp",
        "AQILast.PM25.value": "pm25",
        "AQILast.PM10.value": "pm10",
        "AQILast.O3.value": "o3",
        "AQILast.NO2.value": "no2",
        "AQILast.CO.value": "co",
        "AQILast.SO2.value": "so2",
        "AQILast.AQI.aqi": "aqi"
    }

    # เลือกเฉพาะคอลัมน์ที่มีใน df จริง
    real_rename = {k: v for k, v in rename_map.items() if k in df.columns}

    df = df.rename(columns=real_rename)

    # แปลง timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # แปลงค่าฝุ่นเป็น numeric
    pollutants = ["pm25", "pm10", "o3", "no2", "co", "so2", "aqi"]
    for col in pollutants:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ลบข้อมูลที่ไม่มี timestamp
    df = df.dropna(subset=["timestamp"])

    # กรองเฉพาะสถานีในกรุงเทพ
    df = df[df["area"].str.contains("กรุงเทพ", na=False)]

    # รีเซ็ต index
    df = df.reset_index(drop=True)

    return df
