# tests/test_calculations.py
import pytest
import pandas as pd
from core.transformations import PortfolioTransformer

@pytest.fixture
def mock_blank_fields_data():
    """Generates mock data missing key variables like MODULE, STATE, and BUCKET to test the fallback mechanism."""
    data = {
        "UCIC": ["CUST_TEST_01", "CUST_TEST_02"],
        "CUSTOMERNAME": ["Aarav Sharma", "Aditya Rao"],
        "LOAN_NO": ["LN-PL-101", "LN-HL-301"],
        "LAN_PDT": ["PERSONAL_LOAN", "HOME_LOAN"],
        "DISB_DATE": ["12-04-2024", "11-01-2022"],
        "LAN_DISB_AMT":,
        "LOAN_EMI":,
        "LAN_DPD":,
        "REPAY_MODE": ["ACH", "AUTO_DEBIT"],
        "BRANCH_DESC": ["MUMBAI_FORT", "BANGALORE_WHITEFIELD"],
        "SOLID":,
        "MODULE": ["", "nan"], # Blank values to test the auto-assignment logic
        "STATE": [None, ""],
        "RCLG_ZONE": ["", None]
    }
    return pd.DataFrame(data)

def test_automated_fallback_and_deductions(mock_blank_fields_data):
    """Verifies that empty fields are automatically backfilled by the engine logic."""
    processed = PortfolioTransformer.process_raw_ledger(mock_blank_fields_data)
    
    # 1. Check if MODULE field is successfully inferred from product type
    assert processed.loc[0, "MODULE"] == "RETAIL_UNSECURED"
    assert processed.loc[1, "MODULE"] == "SECURED_MORTGAGES"
    
    # 2. Check if RISK BUCKETS are calculated based on DPD thresholds
    assert int(processed.loc[0, "LAN_BKT"]) == 0
    assert int(processed.loc[1, "LAN_BKT"]) == 4
    
    # 3. Check if spatial identifiers are mapped using branch constants
    assert processed.loc[0, "STATE"] == "MAHARASHTRA"
    assert processed.loc[0, "RCLG_ZONE"] == "WEST_ZONE"
    assert processed.loc[1, "STATE"] == "KARNATAKA"
    assert processed.loc[1, "RCLG_ZONE"] == "SOUTH_ZONE"
