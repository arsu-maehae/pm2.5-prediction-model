import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from fetch_air4thai import fetch_air4thai

@patch('python.fetch_air4thai.requests.get')
def test_fetch_air4thai_success(mock_get):
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "stations": [
            {
                "stationID": "1",
                "nameTH": "Station 1",
                "AQILast": {"PM25": {"value": 10}}
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    df = fetch_air4thai()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

@patch('python.fetch_air4thai.requests.get')
def test_fetch_air4thai_failure(mock_get):
    mock_get.side_effect = Exception("API Error")
    with pytest.raises(Exception):
        fetch_air4thai()