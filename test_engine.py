import pandas as pd
import pytest
import plotly.graph_objects as go
import engine

@pytest.fixture
def mock_portfolio_data():
    """Generates a structured mock dataframe representing edge cases across product types and buckets."""
    data = {
        "UCIC": ["CUST01", "CUST02", "CUST03", "CUST04", "CUST05"],
        "LAN_PDT": ["PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN"],
        "LAN_BKT": [0, 1, 2, 3, 4],
        "EXPOSURE_POS": [10000, 20000, 30000, 40000, 50000],
        "MODULE": ["RETAIL", "RETAIL", "RETAIL", "RETAIL", "RETAIL"],
        "LOAN_NO": ["LN101", "LN102", "LN103", "LN104", "LN105"],
        "CUSTOMERNAME": ["Alice Smith", "Bob Jones", "Charlie Brown", "David Miller", "Emma Davis"],
        "LAN_DISB_AMT": [50000, 50000, 50000, 50000, 50000],
        "REPAY_MODE": ["ACH", "AUTO_DEBIT", "SI", "ACH", "SI"],
        "LOAN_EMI": [2000, 2000, 2000, 2000, 2000],
        "LAN_POS": [40000, 40000, 40000, 40000, 40000],
        "LAN_DPD": [0, 15, 45, 75, 105],
        "LAN_INST_OV_AMT": [0, 2000, 4000, 6000, 8000],
        "OVERDUE_CHARGE": [0, 100, 200, 300, 400],
        "FINAL_ALLO_ID": ["INT_01", "INT_02", "EXT_AG_A", "EXT_AG_B", "LEGAL_01"],
        "RESPONSE_CODE_NEW": ["PTP", "NTP", "RTP", "BP", "LGL"],
        "NPA_TYPE": ["STANDARD", "STANDARD", "SUB_STANDARD", "DOUBTFUL", "LOSS"],
        "WRITEOFF_TAG": ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "WO_POTENTIAL"]
    }
    return pd.DataFrame(data)

def test_compute_bucket_counts(mock_portfolio_data):
    """Ensures business engine extracts exactly accurate volumes per bracket tier."""
    counts = engine.compute_bucket_counts(mock_portfolio_data)
    assert counts["b0"] == 1
    assert counts["b1"] == 1
    assert counts["b2"] == 1
    assert counts["b3"] == 1
    assert counts["b4"] == 1

def test_generate_exposure_plotly_all_products(mock_portfolio_data):
    """Confirms Plotly graph building routines correctly complete on 'ALL PRODUCTS' settings."""
    fig = engine.generate_exposure_plotly(mock_portfolio_data, "[ SHOW ALL PRODUCTS ]")
    
    # 1. Structural Checks: Object must exist and match a valid Plotly Figure
    assert fig is not None
    assert isinstance(fig, go.Figure)
    
    # 2. Data Slicing Check: Ensure chart type is a Pie chart component type
    assert fig.data[0].type == "pie"

def test_generate_exposure_plotly_single_product(mock_portfolio_data):
    """Confirms Plotly graph building routines correctly complete on focused single product categories."""
    filtered_df = mock_portfolio_data[mock_portfolio_data["LAN_PDT"] == "PERSONAL_LOAN"]
    fig = engine.generate_exposure_plotly(filtered_df, "PERSONAL_LOAN")
    
    # 1. Structural Checks: Object must exist and match a valid Plotly Figure
    assert fig is not None
    assert isinstance(fig, go.Figure)
    
    # 2. Functional layout checks: Verify hole size configuration represents a modern donut chart structure
    assert fig.data[0].hole == 0.4
    assert fig.data[0].type == "pie"
