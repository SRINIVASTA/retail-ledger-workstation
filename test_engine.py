import pandas as pd
import pytest
import matplotlib.pyplot as plt
import engine

@pytest.fixture
def mock_portfolio_data():
    """Generates a structured mock dataframe representing edge cases across product types and buckets."""
    data = {
        "UCIC": ["CUST01", "CUST02", "CUST03", "CUST04", "CUST05"],
        "LAN_PDT": ["PERSONAL_LOAN", "CREDIT_CARD", "HOME_LOAN", "PERSONAL_LOAN", "LAP"],
        "LAN_BKT":,  # One instance in each bucket
        "EXPOSURE_POS":,
        "MODULE": ["RETAIL", "CARDS", "MORTGAGE", "RETAIL", "MORTGAGE"],
        "LOAN_NO": ["LN101", "CC202", "HL303", "LN104", "LAP505"],
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
    
    # Asserting count distribution based on fixture setup
    assert counts["b0"] == 1
    assert counts["b1"] == 1
    assert counts["b2"] == 1
    assert counts["b3"] == 1
    assert counts["b4"] == 1


def test_render_metrics_board_html(mock_portfolio_data):
    """Checks if metric panel rendering preserves key styling values and data mappings."""
    html_output = engine.render_metrics_board_html(mock_portfolio_data, "PERSONAL_LOAN")
    
    # Assert structural integrity and data value insertion
    assert "5 Rows" in html_output
    assert "Workspace Ledger state:" in html_output
    assert "Filter: PERSONAL_LOAN" in html_output
    assert "BUCKET 0 (CURRENT)" in html_output


def test_render_audit_inspector_html():
    """Validates structural markup generation when formatting customer profiles."""
    sample_row = {
        "LAN_PDT": "GOLD_LOAN",
        "MODULE": "JEWEL",
        "CUSTOMERNAME": "John Doe",
        "LOAN_NO": "GL-999",
        "LAN_DISB_AMT": 50000,
        "MAKE": "STANDARD",
        "MODEL": "22K_ORNAMENTS",
        "REGDNUM": "VLT-882",
        "HL_NONHL": "NON_HL",
        "LAP_NONLAP": "NON_LAP",
        "REPAY_MODE": "CASH",
        "LOAN_EMI": 1500,
        "LAN_POS": 45000,
        "EXPOSURE_POS": 45000,
        "LAN_DPD": 0,
        "LAN_BKT": 0,
        "LAN_INST_OV_AMT": 0,
        "OVERDUE_CHARGE": 0,
        "FINAL_ALLO_ID": "DESK_04",
        "RESPONSE_CODE_NEW": "PTP",
        "NPA_TYPE": "STANDARD",
        "WRITEOFF_TAG": "ACTIVE"
    }
    
    inspector_html = engine.render_audit_inspector_html("CUST07007", sample_row)
    
    assert "Audit Inspector Panel: CUST07007" in inspector_html
    assert "GOLD_LOAN" in inspector_html
    assert "John Doe" in inspector_html
    assert "₹50,000" in inspector_html


def test_generate_exposure_pie_all_products(mock_portfolio_data):
    """Confirms Matplotlib graph building routines correctly complete on 'ALL PRODUCTS' settings."""
    fig = engine.generate_exposure_pie(mock_portfolio_data, "[ SHOW ALL PRODUCTS ]")
    
    assert fig is not None
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) > 0
    plt.close(fig)  # Safe cleanup memory release


def test_generate_exposure_pie_single_product(mock_portfolio_data):
    """Confirms Matplotlib graph building routines correctly complete on focused single product categories."""
    filtered_df = mock_portfolio_data[mock_portfolio_data["LAN_PDT"] == "PERSONAL_LOAN"]
    fig = engine.generate_exposure_pie(filtered_df, "PERSONAL_LOAN")
    
    assert fig is not None
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) > 0
    plt.close(fig)
