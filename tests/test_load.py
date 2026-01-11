import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from load_postgres import insert_to_postgres

@patch('python.load_postgres.psycopg2.connect')
def test_insert_to_postgres(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_connect.return_value = mock_conn

    df = pd.DataFrame({
        "station_id": ["1"],
        "station_name": ["Station1"],
        "area": ["กรุงเทพ"],
        "timestamp": pd.to_datetime(["2023-01-01"]),
        "pm25": [10]
    })

    insert_to_postgres(df)
    mock_cur.execute.assert_called()
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()