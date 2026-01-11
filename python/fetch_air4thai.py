#ดึงข้อมูล api air4thai และแปลงเป็น DataFrame

import requests
import pandas as pd

API_URL = "http://air4thai.pcd.go.th/services/getNewAQI_JSON.php?region=1"

def fetch_air4thai():
    resp = requests.get(API_URL, timeout=20)
    resp.raise_for_status()
    raw = resp.json()

    # ถ้า JSON มี key "stations" (ตามที่คาด) ให้ใช้มัน
    if isinstance(raw, dict) and "stations" in raw:
        records = raw["stations"]
    # กรณี API ส่ง list โดยตรง
    elif isinstance(raw, list):
        records = raw
    # กรณี JSON ซ้อนแปลกๆ ให้พยายามหา list ใน dict ใดๆ ที่เป็น list ของ dicts
    else:
        records = None
        if isinstance(raw, dict):
            for k, v in raw.items():
                if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    records = v
                    break

    if records is None:
        # เก็บ raw สำหรับ debug และโยน error ชัดๆ
        raise ValueError("ไม่พบ list ของสถานีใน JSON response — โครงสร้าง JSON: {}".format(type(raw)))

    # แปลงเป็น DataFrame (flatten nested dicts)
    df = pd.json_normalize(records)

    # ถ้าคอลัมน์บางอย่างเป็น nested (เช่น pollutant: {value:..., unit:...}) ให้พยายาม flatten เพิ่มเติม
    # (ตัวอย่างโค้ดที่คอยตรวจและ flatten อัตโนมัติ)
    for col in df.columns:
        # ถ้าช่องเป็น dict ในค่าบางแถว ให้ normalize เฉพาะคอลัมน์นั้น
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            expanded = pd.json_normalize(df[col].dropna().tolist())
            # เติม prefix เพื่อไม่ชนกับคอลัมน์อื่น
            expanded = expanded.add_prefix(col + ".")
            df = df.drop(columns=[col]).reset_index(drop=True).join(expanded.reset_index(drop=True))

    return df # คืนค่า DataFrame
