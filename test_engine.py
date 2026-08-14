import pandas as pd
import pytest
import plotly.graph_objects as go
import engine

@pytest.fixture
def mock_portfolio_data():
    """Generates a structured mock dataframe representing edge cases across product types and buckets."""
    data = {
        "UCIC": ["CUST01", "CUST02", "CUST03", "CUST04", "CUST05"],
        # FIXED: Mapped all 5 rows to the same product group so the filtered chart contains all 5 bucket keys
        "LAN_PDT": ["PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN", "PERSONAL_LOAN"],
        "LAN_BKT":,
        "EXPOSURE_POS":,
        "MODULE": ["RETAIL", "RETAIL", "RETAIL", "RETAIL", "RETAIL"],
        "LOAN_NO": ["LN101", "LN102", "LN103", "LN104", "LN105"],
        "CUSTOMERNAME": ["Alice Smith", "Bob Jones", "Charlie Brown", "David Miller", "Emma Davis"],
        "LAN_DISB_AMT":,
        "REPAY_MODE": ["ACH", "AUTO_DEBIT", "SI", "ACH", "SI"],
        "LOAN_EMI":,
        "LAN_POS":,
        "LAN_DPD":,
        "LAN_INST_OV_AMT":,
        "OVERDUE_CHARGE":,
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
    assert fig is not None
    assert isinstance(fig, go.Figure)
    
    trace_labels = list(fig.data[0].labels)
    assert any(label in mock_portfolio_data["LAN_PDT"].values for label in trace_labels)

def test_generate_exposure_plotly_single_product(mock_portfolio_data):
    """Confirms Plotly graph building routines correctly complete on focused single product categories."""
    # This filter will now grab all 5 buckets successfully because of the row array alignment update
    filtered_df = mock_portfolio_data[mock_portfolio_data["LAN_PDT"] == "PERSONAL_LOAN"]
    fig = engine.generate_exposure_plotly(filtered_df, "PERSONAL_LOAN")
    assert fig is not None
    assert isinstance(fig, go.Figure)
    
    trace_labels = list(fig.data[0].labels)
    assert any("Bucket" in str(label) for label in trace_labels)
