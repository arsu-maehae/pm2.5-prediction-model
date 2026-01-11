import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

@patch('load_postgres.psycopg2.connect')
@patch('transform.clean_air_data')
@patch('fetch_air4thai.fetch_air4thai')
def test_main_pipeline(mock_fetch, mock_clean, mock_connect):
    mock_df = pd.DataFrame({'col': [1]})
    mock_fetch.return_value = mock_df
    mock_clean.return_value = pd.DataFrame({
        'station_id': ['1'],
        'station_name': ['Station1'],
        'area': ['กรุงเทพ'],
        'timestamp': pd.to_datetime(['2023-01-01']),
        'pm25': [10]
    })
    mock_conn = mock_connect.return_value
    mock_conn.cursor.return_value = MagicMock()
    mock_conn.commit.return_value = None
    mock_conn.close.return_value = None

    # Import after patching
    import main

    # Check if functions were called
    mock_fetch.assert_called_once()
    mock_clean.assert_called_once_with(mock_df)
    mock_connect.assert_called_once()