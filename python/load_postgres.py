#โหลดข้อมูลเข้าไปในฐานข้อมูล PostgreSQL

import psycopg2
from config import DB_CONFIG

def insert_to_postgres(df):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS air4thai_hourly (
            station_id VARCHAR(10),
            station_name TEXT,
            area TEXT,
            timestamp TIMESTAMP,
            pm25 FLOAT,
            pm10 FLOAT,
            o3 FLOAT,
            no2 FLOAT,
            co FLOAT,
            so2 FLOAT
        );
    """)

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO air4thai_hourly
            (station_id, station_name, area, timestamp, pm25, pm10, o3, no2, co, so2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            row["station_id"],
            row["station_name"],
            row["area"],
            row["timestamp"],
            row.get("pm25"),
            row.get("pm10"),
            row.get("o3"),
            row.get("no2"),
            row.get("co"),
            row.get("so2"),
        ))

    conn.commit()
    conn.close()
