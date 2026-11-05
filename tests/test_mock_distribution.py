# tests/test_mock_distribution.py
import os
import pytest
import pandas as pd
from core.transformations import PortfolioTransformer

@pytest.fixture
def mock_csv_path():
    """Returns the expected path of the corporate portfolio mock CSV file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "loan_master_portfolio_5_buckets.csv")

def test_mock_file_exists(mock_csv_path):
    """Ensures the 20-row reference mock file exists in the directory tree."""
    assert os.path.exists(mock_csv_path), f"Missing target mock validation ledger at: {mock_csv_path}"

def test_geographical_distribution_matrix(mock_csv_path):
    """Verifies the mock dataset maps correctly to the 108 master schema headers."""
    raw_df = pd.read_csv(mock_csv_path)
    processed_df = PortfolioTransformer.process_raw_ledger(raw_df)
    
    # 1. Dimension Matrix Limits Verification
    assert len(processed_df) == 20
    assert len(processed_df.columns) == 108
    
    # 2. Strict Product Allocation Strategy Check (4 Products x 5 Rows Each)
    expected_products = ["PERSONAL_LOAN", "VEHICLE_LOAN", "HOME_LOAN", "LAP"]
    for pdt in expected_products:
        product_slice = processed_df[processed_df["LAN_PDT"] == pdt]
        assert len(product_slice) == 5
        
        # 3. Deterministic Delinquency Bucket Matrix Validation (0 to 4 per product)
        for bkt in range(5):
            bucket_row = product_slice[product_slice["LAN_BKT"] == bkt]
            assert len(bucket_row) == 1

def test_spatial_field_bindings(mock_csv_path):
    """Confirms corporate geographic routing tags parse without missing values."""
    raw_df = pd.read_csv(mock_csv_path)
    processed_df = PortfolioTransformer.process_raw_ledger(raw_df)
    
    # Ensure corporate spatial entries map to target columns without generating blank data
    assert not (processed_df["BRANCH_DESC"] == "NONE").any()
    assert not (processed_df["SOLID"] == "NONE").any()
    assert not (processed_df["STATE"] == "NONE").any()
    assert not (processed_df["RCLG_ZONE"] == "NONE").any()
    
    # Verify auto-calculated cross-mapping targets are matching correctly
    assert (processed_df["UCIC_REGION"] == processed_df["STATE"]).all()
    assert (processed_df["ALLO_ZONES"] == processed_df["RCLG_ZONE"]).all()
