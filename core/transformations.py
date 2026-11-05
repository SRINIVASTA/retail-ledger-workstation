# core/transformations.py [PART 1: Baseline Mathematical Engine & Structural Setup]
import numpy as np
import pandas as pd
from datetime import datetime
import random
from config.constants import MASTER_108_HEADERS, INTEREST_PROFILES, BRANCH_GEOGRAPHY_MAP

class PortfolioTransformer:
    """Processes minimal input templates and expands them into a fully populated 108-column database matrix."""

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
        """Transforms client sheets and maps mock data across all 108 columns."""
        if raw_df is None or raw_df.empty:
            return pd.DataFrame(columns=MASTER_108_HEADERS)
        
        # 1. Initialize full schema skeleton with fallback defaults
        processed_df = pd.DataFrame("NONE", index=raw_df.index, columns=MASTER_108_HEADERS)
        
        # 2. Copy matching available incoming headers
        for col in raw_df.columns:
            if col in processed_df.columns:
                processed_df[col] = raw_df[col]
        
        # Parse core numerical baselines
        if "LAN_BKT" in raw_df.columns:
            processed_df["LAN_BKT"] = pd.to_numeric(raw_df["LAN_BKT"], errors="coerce").fillna(0).astype(int)
        else:
            processed_df["LAN_BKT"] = pd.to_numeric(raw_df.get("LAN_DPD", 0), errors="coerce").apply(
                lambda d: 0 if d <= 0 else (1 if d <= 30 else (2 if d <= 60 else (3 if d <= 90 else 4)))
            )

        numeric_fields = ["LOAN_EMI", "LAN_BKT", "LAN_DPD", "LAN_DISB_AMT"]
        for field in numeric_fields:
            processed_df[field] = pd.to_numeric(processed_df[field], errors="coerce").fillna(0).astype(int)

        # 3. Calculate Core Math Nodes
        processed_df["UCIC_VINTAGE"] = processed_df["DISB_DATE"].apply(cls.calculate_vintage_months)
        processed_df["UCIC_SUB_VINTAGE"] = (processed_df["UCIC_VINTAGE"] - 12).clip(lower=0)
        processed_df["LAN_POS"] = processed_df.apply(cls.amortize_running_balance, axis=1)
        processed_df["EXPOSURE_POS"] = processed_df["LAN_POS"]
        processed_df["LAN_INST_OV_AMT"] = processed_df["LOAN_EMI"] * processed_df["LAN_BKT"]
        processed_df["OVERDUE_CHARGE"] = processed_df["LAN_DPD"].apply(
            lambda d: 0 if d == 0 else (300 if d <= 30 else (800 if d <= 60 else (1200 if d <= 90 else 2500)))
        )

        # 4. Handle Geography and Module Mappings
        def deduce_module(row):
            pdt = str(row.get("LAN_PDT", "")).strip().upper()
            if pdt in ["HOME_LOAN", "LAP"]: return "SECURED_MORTGAGES"
            if pdt == "CREDIT_CARD": return "UNSECURED_CARDS"
            return "RETAIL_UNSECURED"
        processed_df["MODULE"] = processed_df.apply(deduce_module, axis=1)

        def fill_spatial_data(row, target_key: str):
            branch = str(row.get("BRANCH_DESC", "")).strip().upper()
            if branch in BRANCH_GEOGRAPHY_MAP:
                return BRANCH_GEOGRAPHY_MAP[branch][target_key]
            return "WEST_ZONE" if target_key == "RCLG_ZONE" else "MAHARASHTRA"

        processed_df["STATE"] = processed_df.apply(lambda r: fill_spatial_data(r, "STATE"), axis=1)
        processed_df["RCLG_ZONE"] = processed_df.apply(lambda r: fill_spatial_data(r, "RCLG_ZONE"), axis=1)

        # Sync operational tracking column aliases
        processed_df["UCIC_EMI"] = processed_df["LOAN_EMI"]
        processed_df["UCIC_INST_OVD_AMT"] = processed_df["LAN_INST_OV_AMT"]
        processed_df["UCIC_POS"] = processed_df["LAN_POS"]
        processed_df["UCIC_PDT"] = processed_df["LAN_PDT"]
        processed_df["UCIC_DPD"] = processed_df["LAN_DPD"]
        processed_df["UCIC_BUCKET"] = processed_df["LAN_BKT"]
        processed_df["UCIC_DISB_AMT"] = processed_df["LAN_DISB_AMT"]
        processed_df["FINAL_POCKET"] = "BKT_" + processed_df["LAN_BKT"].astype(str)
        processed_df["CYCLE_DATE"] = datetime.today().strftime("%d-%m-%Y")
        processed_df["UCIC_REGION"] = processed_df["STATE"]
        processed_df["UCIC_CITYSTR"] = processed_df["BRANCH_DESC"]
        processed_df["ALLO_REGIONS"] = processed_df["STATE"]
        processed_df["ALLO_ZONES"] = processed_df["RCLG_ZONE"]
# core/transformations.py [PART 2: High-Density Corporate Field Generation & Bureau Metrics Fallbacks]

        # 5. Dynamic Mock Data Generator Filling All Remaining 70 Bureau Headers
        for idx, row in processed_df.iterrows():
            current_bkt = int(row["LAN_BKT"])
            current_dpd = int(row["LAN_DPD"])
            pdt_type = str(row["LAN_PDT"])
            
            # Reconstruct Historical Bureau Delinquency Trend Chains (Months M1 to M5)
            m_bkt = current_bkt
            for m in range(1, 6):
                m_bkt = max(0, m_bkt - random.choice([0, 1])) if current_bkt > 0 else 0
                m_dpd = 0 if m_bkt == 0 else (m_bkt * 30 - random.randint(1, 15))
                
                processed_df.loc[idx, f"M{m}_BKT"] = str(m_bkt)
                processed_df.loc[idx, f"M{m}_DPD"] = str(m_dpd)
                processed_df.loc[idx, f"M{m}_DRE"] = "PTP_KEPT" if m_bkt < 2 else "BROKEN_PTP"
                processed_df.loc[idx, f"M{m}_UNIT_CODE"] = f"UNIT_{row['SOLID']}"

            # General Administrative, Scoring & Product Contextual Tags
            processed_df.loc[idx, "ADDL_INTEREST"] = str(int(row["LAN_POS"] * 0.024)) if current_bkt > 1 else "0"
            processed_df.loc[idx, "BCC_DUE"] = "0"
            processed_df.loc[idx, "BOOK_DIST"] = "METRO" if "MUMBAI" in str(row["BRANCH_DESC"]) else "URBAN"
            processed_df.loc[idx, "NEW_INCOME_SEGMENT"] = random.choice(["SALARIED_MNC", "SELF_EMPLOYED", "HNI_PROFILE"])
            processed_df.loc[idx, "PROMOTIONDESC"] = f"FESTIVE_OFFER_{pdt_type[:3].upper()}"
            processed_df.loc[idx, "SCHEME_DESC"] = f"RETAIL_CLEAN_{pdt_type}"
            processed_df.loc[idx, "UCIC_Phase"] = "PHASE_2"
            processed_df.loc[idx, "DMA_NAME"] = f"AGENCY_DMA_{random.randint(10, 99)}"
            processed_df.loc[idx, "RM_NAME"] = f"OFFICER_RM_{random.randint(100, 990)}"
            processed_df.loc[idx, "Del_Strng"] = f"{current_bkt}-" * 3
            processed_df.loc[idx, "DRE_Strng"] = "STABLE" if current_bkt < 2 else "ALERT_DRE"
            processed_df.loc[idx, "TXNDATE"] = datetime.today().strftime("%Y-%m-%d")
            processed_df.loc[idx, "UCIC_COUNT"] = "1"
            processed_df.loc[idx, "CUST(#)"] = f"CUST-NUM-{row['UCIC'][-3:]}"
            processed_df.loc[idx, "UCIC_EDM_RISK"] = "LOW_RISK" if current_bkt < 2 else ("MEDIUM_RISK" if current_bkt < 4 else "HIGH_RISK")
            processed_df.loc[idx, "RNK"] = "1"
            processed_df.loc[idx, "Hold_Reason"] = "NONE" if current_bkt == 0 else "REPAYMENT_DELAY_PTP"
            processed_df.loc[idx, "PDT_LINKAGE"] = "SINGLE_FACILITY"
            processed_df.loc[idx, "NAME"] = str(row["CUSTOMERNAME"])
            processed_df.loc[idx, "Group"] = "RETAIL_POOL"
            processed_df.loc[idx, "100_LACS_POOL"] = "BELOW_100_LACS"
            processed_df.loc[idx, "M5_ID_Count"] = "1"
            processed_df.loc[idx, "ID_Count"] = "1"
            processed_df.loc[idx, "BANKING_COUNT"] = "12"
            processed_df.loc[idx, "SUCCESS_COUNT"] = "11" if current_bkt > 0 else "12"
            processed_df.loc[idx, "ECS_SUCCESS_PER"] = "91.6" if current_bkt > 0 else "100.0"
            processed_df.loc[idx, "CC_ALLO"] = "0"
            processed_df.loc[idx, "DRE_3M"] = "ACTIVE"
            processed_df.loc[idx, "MAX_DAY_3M"] = str(current_dpd)
            processed_df.loc[idx, "CC_FR_OSP"] = "0"
            processed_df.loc[idx, "CCL_MEGHA_ID"] = f"MEGHA_ID_{random.randint(1000,9999)}"
            processed_df.loc[idx, "PL_CYCLIC"] = "NON_CYCLIC"
            
            # Historic Action Tracking Arrays
            for yr in ["May26", "Apr26", "Mar26", "Feb26", "Jan26", "Dec25"]:
                processed_df.loc[idx, f"RESPONSE_CODE_{yr}"] = "AUTO_DEBIT_SUCCESS" if current_bkt == 0 else "REMINDER_DELIVERED"
                processed_df.loc[idx, f"MAKEDATE_{yr}"] = f"01-{yr[-2:]}-20{yr[-2:]}"

            # Asset & Restructuring Fallbacks
            processed_df.loc[idx, "MAKE"] = "NONE" if pdt_type != "VEHICLE_LOAN" else "MARUTI_SUZUKI"
            processed_df.loc[idx, "MODEL"] = "NONE" if pdt_type != "VEHICLE_LOAN" else "SWIFT_VXI"
            processed_df.loc[idx, "SUBMODEL"] = "NONE" if pdt_type != "VEHICLE_LOAN" else "HATCHBACK_SEGMENT"
            processed_df.loc[idx, f"REGDNUM"] = "NONE" if pdt_type != "VEHICLE_LOAN" else f"MH-12-AB-{random.randint(1000,9999)}"
            processed_df.loc[idx, "HL_NONHL"] = "HL" if pdt_type == "HOME_LOAN" else "NON_HL"
            processed_df.loc[idx, "LAP_NONLAP"] = "LAP" if pdt_type == "LAP" else "NON_LAP"
            processed_df.loc[idx, "FINAL_ALLO_ID"] = f"DESK_OFFICER_{random.randint(1,5)}"
            processed_df.loc[idx, "NPA_TYPE"] = "STANDARD" if current_bkt < 4 else "SUB_STANDARD"
            processed_df.loc[idx, "WRITEOFF_TAG"] = "ACTIVE" if current_bkt < 4 else "WO_POTENTIAL"

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
