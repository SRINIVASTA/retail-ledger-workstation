import pandas as pd
import plotly.express as px

def compute_bucket_counts(df: pd.DataFrame) -> dict:
    """Calculates row counts across all 5 delinquency stages safely."""
    bkt_series = df["LAN_BKT"].astype(str).str.strip()
    return {
        "b0": len(df[bkt_series == "0"]),
        "b1": len(df[df_series == "1"]),
        "b2": len(bkt_series == "2"),
        "b3": len(bkt_series == "3"),
        "b4": len(bkt_series == "4"),
    }

def render_metrics_board_html(df: pd.DataFrame, product_dropdown: str) -> str:
    """Generates the workspace informational alert bar."""
    return f"""
    <div style='background-color: #f6f8fa; border-left: 5px solid #1e3c72; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 20px; font-family: -apple-system,BlinkMacSystemFont; border: 1px solid #d0d7de; border-left-width: 5px;'>
        <span style='font-weight: bold; color: #1e3c72;'>Workspace Ledger State:</span> 
        <span style='color: #2980b9; font-weight: bold;'>Active Portfolio Profile Subsets — Filter: {product_dropdown}</span>
    </div>
    """

def render_audit_inspector_html(target_id: str, row_dict: dict) -> str:
    """Generates the comprehensive 108-Header Cross-Product Audit panel card."""
    return f"""
    <div style='background-color: #ffffff; padding: 15px; border-radius: 6px; border: 1px solid #d0d7de; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;'>
        <h4 style='margin: 0 0 12px 0; background: #1e3c72; color: white; padding: 10px; border-radius: 4px; font-size:14px;'>🛡️ 108-Header Cross-Product Audit Inspector Panel: {target_id}</h4>
        
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

def generate_exposure_plotly(df: pd.DataFrame, product_selection: str):
    """Assembles an interactive Plotly donut chart configuration."""
    if product_selection == "[ SHOW ALL PRODUCTS ]":
        summary = df.groupby("LAN_PDT")["EXPOSURE_POS"].sum().reset_index()
        color_map = {
            "PERSONAL_LOAN": "#2980b9", "CREDIT_CARD": "#8e44ad", "VEHICLE_LOAN": "#27ae60",
            "HOME_LOAN": "#d35400", "GOLD_LOAN": "#f1c40f", "LAP": "#16a085"
        }
        names_col = "LAN_PDT"
        title = "Total Active Capital Exposure Share (Cross-Product Overview)"
    else:
        summary = df.groupby("LAN_BKT")["EXPOSURE_POS"].sum().reset_index()
        summary["BKT_NAME"] = "Bucket " + summary["LAN_BKT"].astype(str)
        color_map = {
            "Bucket 0": "#27ae60", "Bucket 1": "#f1c40f", "Bucket 2": "#e67e22",
            "Bucket 3": "#d35400", "Bucket 4": "#c0392b"
        }
        names_col = "BKT_NAME"
        title = f"Full 5-Stage Capital Exposure Distribution — {product_selection}"

    fig = px.pie(
        summary, values="EXPOSURE_POS", names=names_col,
        color=names_col, color_discrete_map=color_map, hole=0.4
    )
    fig.update_traces(
        textinfo="percent+label", textposition="outside",
        hovertemplate="<b>%{label}</b><br>Exposure: ₹%{value:,.0f}<br>% Share: %{percent}"
    )
    fig.update_layout(
        title={"text": f"<b>{title}</b>", "y": 0.95, "x": 0.5, "xanchor": "center"},
        showlegend=False, margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig
