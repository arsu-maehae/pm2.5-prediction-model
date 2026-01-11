import pandas as pd
import psycopg2
from config import DB_CONFIG
import os

def load_historical_pm25():
    # สร้างตารางใหม่สำหรับข้อมูล historical
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ลบตารางเก่าและสร้างใหม่
    cur.execute("DROP TABLE IF EXISTS pm25_daily_historical;")
    
    cur.execute("""
        CREATE TABLE pm25_daily_historical (
            station_id VARCHAR(10),
            station_name TEXT,
            year INT,
            date DATE,
            pm25 FLOAT,
            PRIMARY KEY (station_id, date)
        );
    """)

    # สร้าง mapping station_id -> station_name จาก air4thai_hourly (case insensitive)
    cur.execute("SELECT DISTINCT LOWER(station_id), station_name FROM air4thai_hourly WHERE station_name IS NOT NULL;")
    station_mapping = {row[0]: row[1] for row in cur.fetchall()}

    # โฟลเดอร์ที่มีไฟล์ Excel
    folder_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'PM2.5')

    for year in range(2011, 2026):  # โหลดทุกปี
        file_path = os.path.join(folder_path, f'PM2.5({year}).xlsx')
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            print(f"Loading {file_path}, columns: {df.columns.tolist()}")

            df.columns = df.columns.str.strip().str.lower()
            if 'date' in df.columns:
                # แปลงเป็น long format: station_id, date, pm25
                station_cols = [col for col in df.columns if col != 'date']
                df_melted = df.melt(id_vars=['date'], value_vars=station_cols, var_name='station_id', value_name='pm25')
                df_melted['station_id'] = df_melted['station_id'].str.lower()  # เช่น 02T -> 02t
                df_melted['pm25'] = pd.to_numeric(df_melted['pm25'], errors='coerce')
                df_melted = df_melted.dropna()

                # Insert เข้าตาราง
                for _, row in df_melted.iterrows():
                    station_name = station_mapping.get(row['station_id'], 'Unknown')
                    cur.execute("""
                        INSERT INTO pm25_daily_historical (station_id, station_name, year, date, pm25)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (station_id, date) DO NOTHING;
                    """, (row['station_id'], station_name, year, row['date'], row['pm25']))

                print(f"Inserted {len(df_melted)} rows for {year}")
            else:
                print(f"Date column not found in {year}")

    conn.commit()
    conn.close()
    print("Historical data loaded successfully.")

if __name__ == "__main__":
    load_historical_pm25()