import pytest
import pandas as pd
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from transform import clean_air_data

def test_clean_air_data():
    # Sample data
    data = {
        "stationID": ["1", "2"],
        "nameTH": ["Station1", "Station2"],
        "areaTH": ["กรุงเทพ", "อื่น"],
        "AQILast.time": ["2023-01-01 12:00:00", "2023-01-01 13:00:00"],
        "AQILast.PM25.value": [10, 20]
    }
    df = pd.DataFrame(data)

    cleaned_df = clean_air_data(df)
    assert "station_id" in cleaned_df.columns
    assert "timestamp" in cleaned_df.columns
    assert cleaned_df["timestamp"].dtype == "datetime64[ns]"
    assert len(cleaned_df) == 1  # Only Bangkok