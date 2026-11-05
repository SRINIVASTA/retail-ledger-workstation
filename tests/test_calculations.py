# tests/test_calculations.py
import pytest
import pandas as pd
from core.transformations import PortfolioTransformer

@pytest.fixture
def mock_portfolio_data():
    data = {
        "UCIC": ["CUST01", "CUST02", "CUST03", "CUST04", "CUST05"],
        "CUSTOMERNAME": ["Alice Smith", "Bob Jones", "Charlie Brown", "David Miller", "Emma Davis"],
        "LOAN_NO": ["LN101", "LN102", "LN103", "LN104", "LN105"],
        "LAN_PDT": ["PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN"],
        "DISB_DATE": ["12-04-2024", "18-09-2024", "05-01-2024", "22-11-2023", "14-06-2023"],
        "LAN_DISB_AMT":,
        "LOAN_EMI":,
        "LAN_BKT":,
        "LAN_DPD":,
        "REPAY_MODE": ["ACH", "AUTO_DEBIT", "SI", "ACH", "SI"],
        "BRANCH_DESC": ["MUMBAI_FORT", "CHENNAI_PARRYS", "DELHI_CONNAUGHT", "KOLKATA_SALT_LAKE", "BANGALORE_MG_ROAD"],
        "SOLID":,
        "STATE": ["MAHARASHTRA", "TAMIL_NADU", "DELHI", "WEST_BENGAL", "KARNATAKA"],
        "RCLG_ZONE": ["WEST_ZONE", "SOUTH_ZONE", "NORTH_ZONE", "EAST_ZONE", "SOUTH_ZONE"]
    }
    return pd.DataFrame(data)

def test_compute_bucket_counts(mock_portfolio_data):
    processed = PortfolioTransformer.process_raw_ledger(mock_portfolio_data)
    counts = PortfolioTransformer.compute_bucket_counts(processed)
    assert counts["b0"] == 1
    assert counts["b1"] == 1
    assert counts["b2"] == 1
    assert counts["b3"] == 1
    assert counts["b4"] == 1
