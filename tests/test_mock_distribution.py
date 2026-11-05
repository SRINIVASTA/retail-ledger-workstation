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
    # Read and process through the data transformation engine
    raw_df = pd.read_csv(mock_csv_path)
    processed_df = PortfolioTransformer.process_raw_ledger(raw_df)
    
    # 1. Dimension Matrix Limits Verification
    assert len(processed_df) == 20, "Enterprise mock dataset must contain exactly 20 rows (4 products x 5 buckets)."
    assert len(processed_df.columns) == 108, "The transformation matrix must expand to exactly 108 corporate columns."
    
    # 2. Strict Product Allocation Strategy Check (4 Products x 5 Rows Each)
    expected_products = ["PERSONAL_LOAN", "VEHICLE_LOAN", "HOME_LOAN", "LAP"]
    for pdt in expected_products:
        product_slice = processed_df[processed_df["LAN_PDT"] == pdt]
        assert len(product_slice) == 5, f"Product group '{pdt}' must have exactly 5 matrix rows."
        
        # 3. Deterministic Delinquency Bucket Matrix Validation (0 to 4 per product)
        for bkt in range(5):
            bucket_row = product_slice[product_slice["LAN_BKT"] == bkt]
            assert len(bucket_row) == 1, f"Product group '{pdt}' must have exactly 1 record allocated to Risk Bucket {bkt}."

def test_spatial_field_bindings(mock_csv_path):
    """Confirms corporate geographic routing tags parse without missing values."""
    raw_df = pd.read_csv(mock_csv_path)
    processed_df = PortfolioTransformer.process_raw_ledger(raw_df)
    
    # Ensure corporate spatial entries map to target columns without generating NaNs or missing strings
    assert not processed_df["BRANCH_DESC"].isna().any(), "Branch Description metrics contain invalid unparsed elements."
    assert not processed_df["SOLID"].isna().any(), "Core banking Sol ID parameters contain unmapped entries."
    assert not processed_df["STATE"].isna().any(), "Jurisdiction State arrays contain unparsed null elements."
    assert not processed_df["RCLG_ZONE"].isna().any(), "Management Regional Zones must not contain null flags."
    
    # Verify auto-calculated cross-mapping targets are matching correctly
    assert (processed_df["UCIC_REGION"] == processed_df["STATE"]).all(), "Geographic region mapping logic drift detected."
    assert (processed_df["ALLO_ZONES"] == processed_df["RCLG_ZONE"]).all(), "Regional zone allocation tracking logic failed verification."
