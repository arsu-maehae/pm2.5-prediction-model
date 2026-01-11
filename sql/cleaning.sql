-- Delete Dups ค่าซ้ำ
DELETE FROM public.air4thai_hourly a
USING public.air4thai_hourly b
WHERE a.ctid < b.ctid
	AND a.station_id = b.station_id
	AND a.timestamp = b.timestamp;

-- Check Outlier  เอาค่าลบออก
UPDATE public.air4thai_hourly
SET pm25 = NULL
WHERE pm25 IS NOT NULL AND pm25 < 0;

UPDATE public.air4thai_hourly
SET pm10 = NULL
WHERE pm10 IS NOT NULL AND pm10 < 0;

UPDATE public.air4thai_hourly
SET o3 = NULL
WHERE o3 IS NOT NULL AND o3 < 0;

UPDATE public.air4thai_hourly
SET no2 = NULL
WHERE no2 IS NOT NULL AND no2 < 0;

UPDATE public.air4thai_hourly
SET co = NULL
WHERE co IS NOT NULL AND co < 0;

UPDATE public.air4thai_hourly
SET so2 = NULL
WHERE so2 IS NOT NULL AND so2 < 0;

-- สร้าง Index ช่วยให้ Query เร็วขึ้น
CREATE INDEX IF NOT EXISTS idx_air_station_time
ON public.air4thai_hourly (station_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_air_timestamp
ON public.air4thai_hourly (timestamp);
