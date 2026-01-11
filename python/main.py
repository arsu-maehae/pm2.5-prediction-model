#รันโปรแกรมทั้งหมด เป็นจุดเริ่มต้นของ pipeline โดยเรียกฟังก์ชันจากไฟล์อื่นๆ ตามลำดับ: 
# ดึงข้อมูล -> ทำความสะอาดข้อมูล -> โหลดเข้า DB

from fetch_air4thai import fetch_air4thai
from transform import clean_air_data
from load_postgres import insert_to_postgres

df = fetch_air4thai()

print(df.columns)
print(df.head())

df = clean_air_data(df)
insert_to_postgres(df)

print("Pipeline completed.")
