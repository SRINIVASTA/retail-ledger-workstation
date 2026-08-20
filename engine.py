import numpy as np
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

MASTER_108_HEADERS = [
    "UCIC", "LOAN_NO", "CUSTOMERNAME", "REPAY_MODE", "UCIC_EMI", "LOAN_EMI", "UCIC_INST_OVD_AMT", 
    "LAN_INST_OV_AMT", "ADDL_INTEREST", "BCC_DUE", "OVERDUE_CHARGE", "UCIC_POS", "LAN_POS", 
    "EXPOSURE_POS", "CYCLE_DATE", "UCIC_DPD", "LAN_DPD", "UCIC_BUCKET", "LAN_BKT", "UCIC_VINTAGE", 
    "UCIC_SUB_VINTAGE", "UCIC_PDT", "LAN_PDT", "BRANCH_DESC", "RCLG_ZONE", "FINAL_POCKET", 
    "UCIC_REGION", "STATE", "UCIC_CITYSTR", "UCIC_Phase", "ALLO_REGIONS", "ALLO_ZONES", "DISB_DATE", 
    "UCIC_DISB_AMT", "LAN_DISB_AMT", "BOOK_DIST", "NEW_INCOME_SEGMENT", "SOLID", "PROMOTIONDESC", 
    "SCHEME_DESC", "MAKE", "MODEL", "SUBMODEL", "REGDNUM", "HL_NONHL", "LAP_NONLAP", "DMA_NAME", 
    "RM_NAME", "Del_Strng", "WRITEOFF_TAG", "DRE_Strng", "TXNDATE", "UCIC_COUNT", "CUST(#)", 
    "UCIC_EDM_RISK", "RNK", "Hold_Reason", "PDT_LINKAGE", "NPA_TYPE", "MODULE", "FINAL_ALLO_ID", 
    "NAME", "Group", "RESPONSE_CODE_NEW", "100_LACS_POOL", "M1_DPD", "M2_DPD", "M3_DPD", "M4_DPD", 
    "M5_DPD", "M1_BKT", "M2_BKT", "M3_BKT", "M4_BKT", "M5_BKT", "M1_DRE", "M2_DRE", "M3_DRE", 
    "M4_DRE", "M5_DRE", "M1_UNIT_CODE", "M2_UNIT_CODE", "M3_UNIT_CODE", "M4_UNIT_CODE", "M5_UNIT_CODE", 
    "M5_ID_Count", "ID_Count", "BANKING_COUNT", "SUCCESS_COUNT", "ECS_SUCCESS_PER", "CC_ALLO", 
    "DRE_3M", "MAX_DAY_3M", "CC_FR_OSP", "RESPONSE_CODE_May26", "MAKEDATE_May26", "RESPONSE_CODE_Apr26", 
    "MAKEDATE_Apr26", "RESPONSE_CODE_Mar26", "MAKEDATE_Mar26", "RESPONSE_CODE_Feb26", "MAKEDATE_Feb26", 
    "RESPONSE_CODE_Jan26", "MAKEDATE_Jan26", "RESPONSE_CODE_Dec25", "MAKEDATE_Dec25", "CCL_MEGHA_ID", "PL_CYCLIC"
]

INTEREST_PROFILES = {
    "CREDIT_CARD": 0.36, "PERSONAL_LOAN": 0.14, "VEHICLE_LOAN": 0.095,
    "HOME_LOAN": 0.085, "LAP": 0.11, "GOLD_LOAN": 0.12
}

def get_field_action_response_code(row) -> str:
    try:
        bkt = int(pd.to_numeric(row.get("LAN_BKT", 0), errors="coerce", downcast="integer"))
        dpd = int(pd.to_numeric(row.get("LAN_DPD", 0), errors="coerce"))
        pdt = str(row.get("LAN_PDT", "PERSONAL_LOAN")).strip().upper()
        ecs_per = float(pd.to_numeric(row.get("ECS_SUCCESS_PER", 100), errors="coerce"))
        max_dpd_3m = int(pd.to_numeric(row.get("MAX_DAY_3M", 0), errors="coerce"))

        if bkt == 0 and dpd == 0:
            return "PAID_VIA_CLEARING"
        if bkt >= 4 or dpd > 90:
            if pdt == "GOLD_LOAN": return "GOLD_JEWELRY_SENT_TO_PUBLIC_AUCTION"
            if pdt == "VEHICLE_LOAN": return "VEHICLE_SEIZED_GARAGE_AUCTION_LISTED"
            if pdt in ["HOME_LOAN", "LAP"]:
                if dpd > 120: return "RECEIVER_APPOINTED_PROPERTY_SEAL_INITIATED"
                return "SARFAESI_POSSESSION_NOTICE_ISSUED"
            if max_dpd_3m > 120: return "ARBITRATION_PROCEEDINGS_INITIATED"
            return "FINAL_LEGAL_DEMAND_NOTICE"
        if bkt == 3 or (60 < dpd <= 90):
            if pdt in ["HOME_LOAN", "LAP", "VEHICLE_LOAN"]: return "HOUSE_LOCKED_ASSET_REPO_TRIGGERED"
            if pdt == "CREDIT_CARD": return "CARD_BLOCKED_EXTERNAL_ASSIGNMENT"
            return "LEGAL_SECTIONS_138_NOTICE_SERVED"
        if bkt == 2 or (30 < dpd <= 60):
            if ecs_per < 40: return "FINAL_REMINDER_LOAN_COLLATERAL"
            if max_dpd_3m > 45: return "LEGAL_NOTICE_UNDER_PREPARATION"
            if pdt in ["PERSONAL_LOAN", "CREDIT_CARD"]: return "VALUATION_AUDIT_COMPLETED"
            return "FIELD_VISIT_ARRANGED"
        if bkt == 1 or (0 < dpd <= 30):
            if ecs_per < 75:
                if max_dpd_3m > 15: return "CARD_LIMIT_TEMPORARY_FREEZE"
                return "REPAYMENT_DELAY_PTP"
            if "REPAYMENT_DELAY_PTP" in str(row.get("Hold_Reason", "")): return "CUSTOMER_PROM_REMITTANCE"
            if pdt == "CREDIT_CARD": return "MARGIN_CALL_SMS_SENT"
            if dpd > 15: return "LEGAL_NOTICE_DELIVERED"
            return "REMINDER_SMS_SENT"
        if ecs_per < 90: return "CASHFLOW_DELAY_PTP"
        if max_dpd_3m > 0: return "SITE_VISIT_COMPLETED_WARNING"
        return "FIELD_VISIT_PENDING"
    except:
        return "PAID_VIA_CLEARING"

def transform_25_to_108_ledger(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=MASTER_108_HEADERS)
    
    processed_df = pd.DataFrame(index=raw_df.index, columns=MASTER_108_HEADERS)
    for col in raw_df.columns:
        if col in processed_df.columns:
            processed_df[col] = raw_df[col]
            
    numeric_fields = ["LOAN_EMI", "LAN_BKT", "LAN_DPD", "LAN_DISB_AMT"]
    for field in numeric_fields:
        processed_df[field] = pd.to_numeric(processed_df[field], errors="coerce").fillna(0).astype(int)

    current_date = datetime.today()

    def compute_vintage_months(disb_val):
        if pd.isna(disb_val) or str(disb_val).strip() in ["", "nan", "NONE"]:
            return 24
        try:
            parsed_d = pd.to_datetime(disb_val, format="%d-%m-%Y", errors='coerce')
            if pd.isna(parsed_d):
                parsed_d = pd.to_datetime(disb_val, errors='coerce')
            if pd.isna(parsed_d): 
                return 24
            months_diff = (current_date.year - parsed_d.year) * 12 + (current_date.month - parsed_d.month)
            return max(1, int(months_diff))
        except:
            return 24

    processed_df["UCIC_VINTAGE"] = processed_df["DISB_DATE"].apply(compute_vintage_months)
    processed_df["UCIC_SUB_VINTAGE"] = (processed_df["UCIC_VINTAGE"] - 12).clip(lower=0)

    def run_financial_amortization(row):
        principal = row["LAN_DISB_AMT"]
        annual_rate = INTEREST_PROFILES.get(str(row["LAN_PDT"]), 0.11)
        monthly_rate = annual_rate / 12
        
        dynamic_vintage = int(row["UCIC_VINTAGE"])
        missed_buckets = int(row["LAN_BKT"])
        cleared_months = max(0, dynamic_vintage - missed_buckets)
        
        running_balance = principal
        for _ in range(cleared_months):
            interest_due = running_balance * monthly_rate
            actual_payment = min(row["LOAN_EMI"], running_balance + interest_due)
            running_balance -= (actual_payment - interest_due)
        return int(max(0, running_balance))

    processed_df["LAN_POS"] = processed_df.apply(run_financial_amortization, axis=1)
    processed_df["EXPOSURE_POS"] = processed_df["LAN_POS"]
    processed_df["LAN_INST_OV_AMT"] = processed_df["LOAN_EMI"] * processed_df["LAN_BKT"]
    processed_df["OVERDUE_CHARGE"] = processed_df["LAN_DPD"].apply(
        lambda d: 0 if d == 0 else (300 if d <= 30 else (800 if d <= 60 else (1200 if d <= 90 else 2500)))
    )

    processed_df["UCIC_EMI"] = processed_df["LOAN_EMI"]
    processed_df["UCIC_INST_OVD_AMT"] = processed_df["LAN_INST_OV_AMT"]
    processed_df["UCIC_POS"] = processed_df["LAN_POS"]
    processed_df["UCIC_PDT"] = processed_df["LAN_PDT"]
    processed_df["UCIC_DPD"] = processed_df["LAN_DPD"]
    processed_df["UCIC_BUCKET"] = processed_df["LAN_BKT"]
    processed_df["UCIC_DISB_AMT"] = processed_df["LAN_DISB_AMT"]
    processed_df["FINAL_POCKET"] = "BKT_" + processed_df["LAN_BKT"].astype(str)
    processed_df["CYCLE_DATE"] = current_date.strftime("%d-%m-%Y")
    processed_df["RESPONSE_CODE_NEW"] = processed_df.apply(get_field_action_response_code, axis=1)

    text_targets = ["MAKE", "MODEL", "SUBMODEL", "REGDNUM", "WRITEOFF_TAG", "NPA_TYPE", "MODULE", "FINAL_ALLO_ID"]
    for column in text_targets:
        processed_df[column] = processed_df[column].astype(str).str.replace(".0", "", regex=False).str.strip()
        processed_df[column] = processed_df[column].apply(lambda x: "NONE" if x in ["nan", "", "0"] else x)
    return processed_df

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
def generate_exposure_plotly(df: pd.DataFrame, product_selection: str):
    if product_selection == "[ SHOW ALL PRODUCTS ]":
        summary = df.groupby("LAN_PDT")["EXPOSURE_POS"].sum().reset_index()
        color_map = {"PERSONAL_LOAN": "#2980b9", "CREDIT_CARD": "#8e44ad", "VEHICLE_LOAN": "#27ae60", "HOME_LOAN": "#d35400", "GOLD_LOAN": "#f1c40f", "LAP": "#16a085"}
        names_col = "LAN_PDT"
        title = "Total Active Capital Exposure Share"
    else:
        summary = df.groupby("LAN_BKT")["EXPOSURE_POS"].sum().reset_index()
        summary["BKT_NAME"] = "Bucket " + summary["LAN_BKT"].astype(str)
        color_map = {"Bucket 0": "#27ae60", "Bucket 1": "#f1c40f", "Bucket 2": "#e67e22", "Bucket 3": "#d35400", "Bucket 4": "#c0392b"}
        names_col = "BKT_NAME"
        title = f"Capital Exposure Distribution — {product_selection}"

    fig = px.pie(summary, values="EXPOSURE_POS", names=names_col, color=names_col, color_discrete_map=color_map, hole=0.4)
    fig.update_traces(textinfo="percent+label", textposition="outside", hovertemplate="<b>%{label}</b><br>Exposure: ₹%{value:,.0f}<br>% Share: %{percent}")
    fig.update_layout(title={"text": f"<b>{title}</b>", "y": 0.95, "x": 0.5, "xanchor": "center"}, showlegend=False, margin=dict(t=60, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def generate_audit_pdf(target_id: str, row_dict: dict, allocation_strategy: str = "MONITORING LOG") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor("#1e3c72"), spaceAfter=15, alignment=1)
    section_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#2a5298"), spaceBefore=10, spaceAfter=4)
    cell_label_style = ParagraphStyle('CellLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#4a5568"))
    cell_value_style = ParagraphStyle('CellValue', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#1a202c"))
    strategy_style = ParagraphStyle('StrategyText', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=13, textColor=colors.HexColor("#2d3748"))

    story.append(Paragraph("CREDITPULSE AI — MASTER COMPLIANCE AUDIT REPORT", title_style))
    story.append(Paragraph(f"<b>Audit Key (UCIC):</b> {target_id} | Session Date: {datetime.today().strftime('%Y-%m-%d')}", cell_value_style))
    story.append(Spacer(1, 10))
    
    def safe_convert(val):
        try: return int(float(val))
        except: return 0

    bkt = safe_convert(row_dict.get('LAN_BKT', 0))
    emi = safe_convert(row_dict.get('LOAN_EMI', 0))
    dpd = safe_convert(row_dict.get('LAN_DPD', 0))
    vintage = safe_convert(row_dict.get('UCIC_VINTAGE', 24))
    
    # Map raw bucket states to precise workspace risk tier classifications
    risk_tiers = {
        0: "STANDARD / PERFORMING ASSET",
        1: "SMA-0 / SPECIAL MENTION ACCOUNT",
        2: "SMA-1 / EARLY WARNING SUBSET",
        3: "SMA-2 / HIGH RISK OUTLIER",
        4: "NPA / NON-PERFORMING SUBSTANDARD"
    }
    current_tier = risk_tiers.get(bkt, "NPA / NON-PERFORMING SUBSTANDARD")
    dynamic_response_tag = row_dict.get('RESPONSE_CODE_NEW', get_field_action_response_code(row_dict))

    story.append(Paragraph("1. Risk Regulatory Status Metrics", section_style))
    meta_data = [
        [Paragraph("Regulatory Bucket Code:", cell_label_style), Paragraph(f"BUCKET_{bkt}", cell_value_style), Paragraph("Portfolio Risk Tier:", cell_label_style), Paragraph(current_tier, cell_value_style)],
        [Paragraph("Product Group (LAN_PDT):", cell_label_style), Paragraph(str(row_dict.get('LAN_PDT')), cell_value_style), Paragraph("Module Category:", cell_label_style), Paragraph(str(row_dict.get('MODULE', 'SECURED_MORTGAGES')), cell_value_style)],
        [Paragraph("Customer Name:", cell_label_style), Paragraph(str(row_dict.get('CUSTOMERNAME')), cell_value_style), Paragraph("Loan Account No:", cell_label_style), Paragraph(str(row_dict.get('LOAN_NO')), cell_value_style)],
        [Paragraph("Original Disbursal Date:", cell_label_style), Paragraph(str(row_dict.get('DISB_DATE')), cell_value_style), Paragraph("Calculated Loan Tenure:", cell_label_style), Paragraph(f"{vintage} Months Active", cell_value_style)]
    ]
    t1 = Table(meta_data, colWidths=)
    t1.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0"))]))
    story.append(t1)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Financial Balances & Field Allocations", section_style))
    sect_data = [
        [Paragraph("Original Disbursed Principal:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('LAN_DISB_AMT', 0)):,}", cell_value_style), Paragraph("Live Computed Balance (POS):", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('LAN_POS', 0)):,}", cell_value_style)],
        [Paragraph("Contractual Scheduled EMI:", cell_label_style), Paragraph(f"₹{emi:,}", cell_value_style), Paragraph("Total Exposure POS Risk:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('EXPOSURE_POS', 0)):,}", cell_value_style)],
        [Paragraph("Days Past Due (LAN_DPD):", cell_label_style), Paragraph(f"{dpd} Days", cell_value_style), Paragraph("Total Overdue Principal:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('LAN_INST_OV_AMT', 0)):,}", cell_value_style)],
        [Paragraph("Field Action Response Code:", cell_label_style), Paragraph(f"<b>{dynamic_response_tag}</b>", cell_value_style), Paragraph("Late Presentation Penalty Fees:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('OVERDUE_CHARGE', 0)):,}", cell_value_style)]
    ]
    t2 = Table(sect_data, colWidths=)
    t2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0"))]))
    story.append(t2)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Official Mandated Playbook Strategy Directive", section_style))
    story.append(Paragraph(str(allocation_strategy), strategy_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
