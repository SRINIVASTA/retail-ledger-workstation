# core/transformations.py
import numpy as np
import pandas as pd
from datetime import datetime
from config.constants import MASTER_108_HEADERS, INTEREST_PROFILES, BRANCH_GEOGRAPHY_MAP

class PortfolioTransformer:
    """Transforms raw minimal files and fills missing corporate dimensions programmatically."""

    @staticmethod
    def calculate_vintage_months(disb_date_val) -> int:
        if pd.isna(disb_date_val) or str(disb_date_val).strip() in ["", "nan", "NONE"]:
            return 24
        try:
            parsed_d = pd.to_datetime(disb_date_val, format="%d-%m-%Y", errors='coerce')
            if pd.isna(parsed_d):
                parsed_d = pd.to_datetime(disb_date_val, errors='coerce')
            if pd.isna(parsed_d): 
                return 24
            current_date = datetime.today()
            months_diff = (current_date.year - parsed_d.year) * 12 + (current_date.month - parsed_d.month)
            return max(1, int(months_diff))
        except Exception:
            return 24

    @classmethod
    def amortize_running_balance(cls, row: pd.Series) -> int:
        try:
            principal = int(float(row.get("LAN_DISB_AMT", 0)))
            if principal <= 0:
                # Secondary fallback if Disbursed Amt is missing: reconstruct via baseline estimates
                principal = int(float(row.get("LOAN_EMI", 10000))) * 24
            
            annual_rate = INTEREST_PROFILES.get(str(row.get("LAN_PDT", "PERSONAL_LOAN")), 0.11)
            monthly_rate = annual_rate / 12
            
            vintage = int(row.get("UCIC_VINTAGE", 24))
            buckets = int(row.get("LAN_BKT", 0))
            cleared_months = max(0, vintage - buckets)
            emi = float(row.get("LOAN_EMI", 0))
            
            running_balance = principal
            for _ in range(cleared_months):
                interest_due = running_balance * monthly_rate
                payment = min(emi, running_balance + interest_due)
                running_balance -= (payment - interest_due)
            return int(max(0, running_balance))
        except Exception:
            return 0

    @classmethod
    def process_raw_ledger(cls, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Transforms client templates into full 108 column outputs with automated backfills."""
        if raw_df is None or raw_df.empty:
            return pd.DataFrame(columns=MASTER_108_HEADERS)
        
        processed_df = pd.DataFrame(index=raw_df.index, columns=MASTER_108_HEADERS)
        for col in raw_df.columns:
            if col in processed_df.columns:
                processed_df[col] = raw_df[col]
        
        # 1. Fallback Rule Engine: Calculate missing Risk Buckets if empty but DPD is present
        if "LAN_BKT" in raw_df.columns:
            def deduce_bucket(row):
                val = str(row.get("LAN_BKT", "")).strip()
                if val in ["", "nan", "None", "NONE"]:
                    dpd = pd.to_numeric(row.get("LAN_DPD", 0), errors="coerce")
                    dpd = 0 if pd.isna(dpd) else dpd
                    return 0 if dpd <= 0 else (1 if dpd <= 30 else (2 if dpd <= 60 else (3 if dpd <= 90 else 4)))
                return pd.to_numeric(val, errors="coerce")
            processed_df["LAN_BKT"] = raw_df.apply(deduce_bucket, axis=1)
        else:
            processed_df["LAN_BKT"] = pd.to_numeric(raw_df.get("LAN_DPD", 0), errors="coerce").apply(
                lambda d: 0 if d <= 0 else (1 if d <= 30 else (2 if d <= 60 else (3 if d <= 90 else 4)))
            )

        # Enforce baseline clean numerical structures
        numeric_fields = ["LOAN_EMI", "LAN_BKT", "LAN_DPD", "LAN_DISB_AMT"]
        for field in numeric_fields:
            processed_df[field] = pd.to_numeric(processed_df[field], errors="coerce").fillna(0).astype(int)

        # 2. Fallback Rule Engine: Resolve blank MODULE allocations based on Product Type
        def deduce_module(row):
            mod_val = str(row.get("MODULE", "")).strip()
            if mod_val not in ["", "nan", "None", "NONE", "0"]:
                return mod_val
            pdt = str(row.get("LAN_PDT", "")).strip().upper()
            if pdt in ["HOME_LOAN", "LAP"]:
                return "SECURED_MORTGAGES"
            if pdt == "CREDIT_CARD":
                return "UNSECURED_CARDS"
            return "RETAIL_UNSECURED"
        processed_df["MODULE"] = raw_df.apply(deduce_module, axis=1)

        # 3. Fallback Rule Engine: Resolve empty STATE or RCLG_ZONE indices from Branch Description
        def fill_spatial_data(row, target_key: str):
            current_val = str(row.get(target_key, "")).strip()
            if current_val not in ["", "nan", "None", "NONE"]:
                return current_val
            branch = str(row.get("BRANCH_DESC", "")).strip().upper()
            if branch in BRANCH_GEOGRAPHY_MAP:
                return BRANCH_GEOGRAPHY_MAP[branch][target_key]
            return "WEST_ZONE" if target_key == "RCLG_ZONE" else "MAHARASHTRA"

        processed_df["STATE"] = raw_df.apply(lambda r: fill_spatial_data(r, "STATE"), axis=1)
        processed_df["RCLG_ZONE"] = raw_df.apply(lambda r: fill_spatial_data(r, "RCLG_ZONE"), axis=1)

        # Execute temporal processing loops
        processed_df["UCIC_VINTAGE"] = processed_df["DISB_DATE"].apply(cls.calculate_vintage_months)
        processed_df["UCIC_SUB_VINTAGE"] = (processed_df["UCIC_VINTAGE"] - 12).clip(lower=0)
        
        # Calculate Amortized Principal Balance (POS)
        processed_df["LAN_POS"] = processed_df.apply(cls.amortize_running_balance, axis=1)
        processed_df["EXPOSURE_POS"] = processed_df["LAN_POS"]
        
        # Sync transactional deltas
        processed_df["LAN_INST_OV_AMT"] = processed_df["LOAN_EMI"] * processed_df["LAN_BKT"]
        processed_df["OVERDUE_CHARGE"] = processed_df["LAN_DPD"].apply(
            lambda d: 0 if d == 0 else (300 if d <= 30 else (800 if d <= 60 else (1200 if d <= 90 else 2500)))
        )

        # Mirror technical database fields
        processed_df["UCIC_EMI"] = processed_df["LOAN_EMI"]
        processed_df["UCIC_INST_OVD_AMT"] = processed_df["LAN_INST_OV_AMT"]
        processed_df["UCIC_POS"] = processed_df["LAN_POS"]
        processed_df["UCIC_PDT"] = processed_df["LAN_PDT"]
        processed_df["UCIC_DPD"] = processed_df["LAN_DPD"]
        processed_df["UCIC_BUCKET"] = processed_df["LAN_BKT"]
        processed_df["UCIC_DISB_AMT"] = processed_df["LAN_DISB_AMT"]
        processed_df["FINAL_POCKET"] = "BKT_" + processed_df["LAN_BKT"].astype(str)
        processed_df["CYCLE_DATE"] = datetime.today().strftime("%d-%m-%Y")
        
        # Synchronize geographical routing variables
        processed_df["UCIC_REGION"] = processed_df["STATE"]
        processed_df["UCIC_CITYSTR"] = processed_df["BRANCH_DESC"]
        processed_df["ALLO_REGIONS"] = processed_df["STATE"]
        processed_df["ALLO_ZONES"] = processed_df["RCLG_ZONE"]

        text_targets = ["MAKE", "MODEL", "SUBMODEL", "REGDNUM", "WRITEOFF_TAG", "NPA_TYPE", "FINAL_ALLO_ID"]
        for column in text_targets:
            processed_df[column] = processed_df[column].astype(str).str.replace(".0", "", regex=False).str.strip()
            processed_df[column] = processed_df[column].apply(lambda x: "NONE" if x in ["nan", "", "0"] else x)
            
        return processed_df

    @staticmethod
    def compute_bucket_counts(df: pd.DataFrame) -> dict:
        if df is None or df.empty: 
            return {"b0": 0, "b1": 0, "b2": 0, "b3": 0, "b4": 0}
        bkt_series = df["LAN_BKT"].astype(int)
        return {
            "b0": len(df[bkt_series == 0]), 
            "b1": len(df[bkt_series == 1]), 
            "b2": len(df[bkt_series == 2]), 
            "b3": len(df[bkt_series == 3]), 
            "b4": len(df[bkt_series >= 4])
        }
