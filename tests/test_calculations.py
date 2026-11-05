# tests/test_calculations.py
import pytest
import pandas as pd
from core.transformations import PortfolioTransformer

@pytest.fixture
def mock_blank_fields_data():
    """Generates a structurally complete mock dataframe with empty targets to validate fallback behavior."""
    data = {
        "UCIC": ["CUST_TEST_01", "CUST_TEST_02"],
        "CUSTOMERNAME": ["Aarav Sharma", "Aditya Rao"],
        "LOAN_NO": ["LN-PL-101", "LN-HL-301"],
        "LAN_PDT": ["PERSONAL_LOAN", "HOME_LOAN"],
        "DISB_DATE": ["12-04-2024", "11-01-2022"],
        "LAN_DISB_AMT":,          # 🟢 FIXED: Fully populated array values
        "LOAN_EMI":,                  # 🟢 FIXED: Fully populated array values
        "LAN_DPD":,                           # 🟢 FIXED: Fully populated array values
        "REPAY_MODE": ["ACH", "AUTO_DEBIT"],
        "BRANCH_DESC": ["MUMBAI_FORT", "BANGALORE_WHITEFIELD"],
        "SOLID":,                        # 🟢 FIXED: Fully populated array values
        "MODULE": ["", "nan"],
        "STATE": [None, ""],
        "RCLG_ZONE": ["", None]
    }
    return pd.DataFrame(data)

def test_automated_fallback_and_deductions(mock_blank_fields_data):
    """Verifies that empty string fields are correctly backfilled by the engine logic."""
    processed = PortfolioTransformer.process_raw_ledger(mock_blank_fields_data)
    
    # 1. Structural Class Inferences Verification
    assert processed.loc[0, "MODULE"] == "RETAIL_UNSECURED"
    assert processed.loc[1, "MODULE"] == "SECURED_MORTGAGES"
    
    # 2. Continuous Delinquency Bracket Verification
    assert int(processed.loc[0, "LAN_BKT"]) == 0
    assert int(processed.loc[1, "LAN_BKT"]) == 4
    
    # 3. Spatial Branch Routing Constants Verification
    assert processed.loc[0, "STATE"] == "MAHARASHTRA"
    assert processed.loc[0, "RCLG_ZONE"] == "WEST_ZONE"
    assert processed.loc[1, "STATE"] == "KARNATAKA"
    assert processed.loc[1, "RCLG_ZONE"] == "SOUTH_ZONE"

def test_complete_108_header_population_matrix(mock_blank_fields_data):
    """Ensures no columns return blank spaces and historical bureau lists are initialized."""
    processed = PortfolioTransformer.process_raw_ledger(mock_blank_fields_data)
    
    # 1. Dimensional Limit Verification
    assert len(processed.columns) == 108
    
    # 2. Bureau Trend Chain Instantiation Verification
    assert processed.loc[0, "M1_BKT"] != "NONE"
    assert processed.loc[0, "M5_DPD"] != "NONE"
    assert processed.loc[1, "M1_UNIT_CODE"] == "UNIT_5602"
