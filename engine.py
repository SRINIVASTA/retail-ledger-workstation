import matplotlib.pyplot as plt
import pandas as pd


def compute_bucket_counts(df: pd.DataFrame) -> dict:
    """Calculates row counts across all 5 delinquency stages."""
    return {
        "b0": len(df[df["LAN_BKT"] == 0]),
        "b1": len(df[df["LAN_BKT"] == 1]),
        "b2": len(df[df["LAN_BKT"] == 2]),
        "b3": len(df[df["LAN_BKT"] == 3]),
        "b4": len(df[df["LAN_BKT"] == 4]),
    }


def render_metrics_board_html(df: pd.DataFrame, product_dropdown: str) -> str:
    """Generates the main KPI dashboard metrics grid banner."""
    counts = compute_bucket_counts(df)
    return f"""
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin-bottom: 20px; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial;'>
        <div style='background-color: #2c3e50; color: white; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size: 11px; font-weight: bold; text-transform: uppercase; opacity: 0.8;'>📊 CURRENT FILTERED</div>
            <div style='font-size: 20px; font-weight: bold; margin-top: 4px;'>{len(df)} Rows</div>
        </div>
        <div style='background-color: #27ae60; color: white; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size: 11px; font-weight: bold; text-transform: uppercase; opacity: 0.8;'>🟢 BUCKET 0 (CURRENT)</div>
            <div style='font-size: 20px; font-weight: bold; margin-top: 4px;'>{counts['b0']} Rows</div>
        </div>
        <div style='background-color: #f1c40f; color: #2c3e50; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size: 11px; font-weight: bold; text-transform: uppercase; opacity: 0.8;'>🟡 BUCKET 1 (1-30)</div>
            <div style='font-size: 20px; font-weight: bold; margin-top: 4px;'>{counts['b1']} Rows</div>
        </div>
        <div style='background-color: #e67e22; color: white; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size: 11px; font-weight: bold; text-transform: uppercase; opacity: 0.8;'>🟠 BUCKET 2 (31-60)</div>
            <div style='font-size: 20px; font-weight: bold; margin-top: 4px;'>{counts['b2']} Rows</div>
        </div>
        <div style='background-color: #d35400; color: white; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size: 11px; font-weight: bold; text-transform: uppercase; opacity: 0.8;'>🔴 BUCKET 3 (61-90)</div>
            <div style='font-size: 20px; font-weight: bold; margin-top: 4px;'>{counts['b3']} Rows</div>
        </div>
        <div style='background-color: #c0392b; color: white; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size: 11px; font-weight: bold; text-transform: uppercase; opacity: 0.8;'>☠️ BUCKET 4 (91+)</div>
            <div style='font-size: 20px; font-weight: bold; margin-top: 4px;'>{counts['b4']} Rows</div>
        </div>
    </div>
    <div style='background-color: #f6f8fa; border-left: 5px solid #2c3e50; padding: 8px 16px; border-radius: 0 6px 6px 0; margin-bottom: 20px; font-family: -apple-system,BlinkMacSystemFont; border: 1px solid #d0d7de; border-left-width: 5px;'>
        <span style='font-weight: bold; color: #2c3e50;'>Workspace Ledger state:</span> 
        <span style='color: #2980b9; font-weight: bold;'>Active Portfolio Profile Subsets — Filter: {product_dropdown}</span>
    </div>
    """


def render_audit_inspector_html(target_id: str, row_dict: dict) -> str:
    """Generates the comprehensive 108-Header Cross-Product Audit panel card."""
    return f"""
    <div style='background-color: #ffffff; padding: 15px; border-radius: 6px; border: 1px solid #d0d7de; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;'>
        <h4 style='margin: 0 0 12px 0; background: #2c3e50; color: white; padding: 10px; border-radius: 4px; font-size:14px;'>🛡️ 108-Header Cross-Product Audit Inspector Panel: {target_id}</h4>
        
        <h5 style='color: #2980b9; margin: 10px 0 5px 0; border-bottom: 2px solid #3498db; padding-bottom:3px;'>🏷️ Sourcing & Identification Parameters</h5>
        <table style='width: 100%; font-size: 13px; margin-bottom:10px;'>
            <tr><td style='width:50%'><b>LAN_PDT (Product Group):</b> <mark style='font-weight:bold; background-color:#fff5b1;'>{row_dict.get('LAN_PDT','')}</mark></td><td><b>MODULE CATEGORY:</b> {row_dict.get('MODULE','')}</td></tr>
            <tr><td><b>CUSTOMERNAME:</b> {row_dict.get('CUSTOMERNAME','')}</td><td><b>LOAN_ACCOUNT_NO:</b> {row_dict.get('LOAN_NO','')}</td></tr>
            <tr><td><b>ORIGINAL DISBURSAL DATE:</b> {row_dict.get('DISB_DATE','')}</td><td><b>DISBURSED PRINCIPAL:</b> ₹{int(row_dict.get('LAN_DISB_AMT', 0)):,}</td></tr>
        </table>
        
        <h5 style='color: #27ae60; margin: 15px 0 5px 0; border-bottom: 2px solid #2ecc71; padding-bottom:3px;'>🏠 Collateral Asset Verification Parameters</h5>
        <table style='width: 100%; font-size: 13px; background: #f6f8fa; padding: 8px; border-radius:4px; margin-bottom:10px;'>
            <tr><td style='width:50%'><b>MAKE / RESTRUCTURING:</b> {row_dict.get('MAKE','')}</td><td><b>ASSET MODEL / SEGMENT:</b> {row_dict.get('MODEL','')}</td></tr>
            <tr><td><b>REGISTRATION/VAULT REFS (REGDNUM):</b> {row_dict.get('REGDNUM','')}</td><td><b>HL / LAP FLAGS:</b> {row_dict.get('HL_NONHL','')} | {row_dict.get('LAP_NONLAP','')}</td></tr>
        </table>
        
        <h5 style='color: #e67e22; margin: 15px 0 5px 0; border-bottom: 2px solid #e67e22; padding-bottom:3px;'>💳 Monthly Billing & Active Balances</h5>
        <table style='width: 100%; font-size: 13px; margin-bottom:10px;'>
            <tr><td style='width:50%'><b>GATEWAY PRESENTATION MODE:</b> {row_dict.get('REPAY_MODE','')}</td><td><b>LOAN SCHEDULED EMI:</b> ₹{int(row_dict.get('LOAN_EMI', 0)):,}</td></tr>
            <tr><td><b>PRINCIPAL BAL (LAN_POS):</b> ₹{int(row_dict.get('LAN_POS', 0)):,}</td><td><b>TOTAL EXPOSURE POS RISK:</b> ₹{int(row_dict.get('EXPOSURE_POS', 0)):,}</td></tr>
        </table>
        
        <h5 style='color: #c0392b; margin: 15px 0 5px 0; border-bottom: 2px solid #e74c3c; padding-bottom:3px;'>🚨 Delinquency Buckets & Field Allocations</h5>
        <table style='width: 100%; font-size: 13px;'>
            <tr><td style='width:50%'><b>DAYS PAST DUE (LAN_DPD):</b> <span style='color:red; font-weight:bold;'>{row_dict.get('LAN_DPD','')} days</span></td><td><b>RISK BUCKET:</b> Bucket {row_dict.get('LAN_BKT','')}</td></tr>
            <tr><td><b>TOTAL OVERDUE PRINCIPAL BAL:</b> ₹{int(row_dict.get('LAN_INST_OV_AMT', 0)):,}</td><td><b>LATE PRESENTATION FEES:</b> ₹{int(row_dict.get('OVERDUE_CHARGE', 0)):,}</td></tr>
            <tr><td><b>ASSIGNED AGENCY ID DESK:</b> {row_dict.get('FINAL_ALLO_ID','')}</td><td><b>FIELD ACTION CODES (RESPONSE):</b> <i>{row_dict.get('RESPONSE_CODE_NEW','')}</i></td></tr>
            <tr><td><b>NPA STATUS CODE:</b> <b>{row_dict.get('NPA_TYPE','')}</b></td><td><b>ACCOUNT WRITEOFF STATUS:</b> <b>{row_dict.get('WRITEOFF_TAG','')}</b></td></tr>
        </table>
    </div>
    """


def generate_exposure_pie(df: pd.DataFrame, product_selection: str):
    """Assembles the tailored Matplotlib exposure donut chart configuration."""
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(6.5, 5), facecolor="white")

    if product_selection == "[ SHOW ALL PRODUCTS ]":
        summary = df.groupby("LAN_PDT")["EXPOSURE_POS"].sum().reset_index()
        palette = {
            "PERSONAL_LOAN": "#2980b9",
            "CREDIT_CARD": "#8e44ad",
            "VEHICLE_LOAN": "#27ae60",
            "HOME_LOAN": "#d35400",
            "GOLD_LOAN": "#f1c40f",
            "LAP": "#16a085",
        }
        colors = [palette.get(x, "#2c3e50") for x in summary["LAN_PDT"]]
        labels = [
            f"{row['LAN_PDT']}\n(₹{int(row['EXPOSURE_POS']):,})"
            for _, row in summary.iterrows()
        ]
        title = "Total Active Capital Exposure Share Breakdown\n(Cross-Product Overview)"
    else:
        summary = df.groupby("LAN_BKT")["EXPOSURE_POS"].sum().reset_index()
        summary["BKT_NAME"] = "Bucket " + summary["LAN_BKT"].astype(str)
        palette = {
            "Bucket 0": "#27ae60",
            "Bucket 1": "#f1c40f",
            "Bucket 2": "#e67e22",
            "Bucket 3": "#d35400",
            "Bucket 4": "#c0392b",
        }
        colors = [palette.get(x, "#7f8c8d") for x in summary["BKT_NAME"]]
        labels = [
            f"{row['BKT_NAME']}\n(₹{int(row['EXPOSURE_POS']):,})"
            for _, row in summary.iterrows()
        ]
        title = f"Full 5-Stage Capital Exposure Share Distribution\n{product_selection}"

    ax.pie(
        summary["EXPOSURE_POS"],
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.75,
        textprops={"fontsize": 8, "fontweight": "bold"},
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=1.5),
    )
    ax.set_title(title, fontsize=10, fontweight="bold", color="#2c3e50")
    plt.tight_layout()
    return fig
