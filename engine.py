import numpy as np
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Complete Master Blueprint Configuration Schema
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

def transform_25_to_108_ledger(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Takes a 25-header raw asset upload and builds out the missing 83 target fields automatically."""
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=MASTER_108_HEADERS)
    
    processed_df = pd.DataFrame(index=raw_df.index, columns=MASTER_108_HEADERS)
    
    for col in raw_df.columns:
        if col in processed_df.columns:
            processed_df[col] = raw_df[col]
            
    if "CUST(#)" not in raw_df.columns or raw_df["CUST(#)"].isna().all():
        if "UCIC" in raw_df.columns:
            processed_df["CUST(#)"] = raw_df["UCIC"].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
        else:
            processed_df["CUST(#)"] = range(1, len(raw_df) + 1)

    processed_df["LOAN_EMI"] = pd.to_numeric(processed_df["LOAN_EMI"], errors="coerce").fillna(0).astype(int)
    processed_df["LAN_BKT"] = pd.to_numeric(processed_df["LAN_BKT"], errors="coerce").fillna(0).astype(int)
    processed_df["LAN_DPD"] = pd.to_numeric(processed_df["LAN_DPD"], errors="coerce").fillna(0).astype(int)
    processed_df["EXPOSURE_POS"] = pd.to_numeric(processed_df["EXPOSURE_POS"], errors="coerce").fillna(0)

    # Core Dynamic Fields Auto-Generation Strategy
    processed_df["LAN_INST_OV_AMT"] = processed_df["LAN_INST_OV_AMT"].fillna(processed_df["LOAN_EMI"] * processed_df["LAN_BKT"])
    processed_df["OVERDUE_CHARGE"] = processed_df.apply(
        lambda r: 0 if r["LAN_DPD"] == 0 else (
            300 if r["LAN_DPD"] <= 30 else (800 if r["LAN_DPD"] <= 60 else (1200 if r["LAN_DPD"] <= 90 else 2500))
        ), axis=1
    )

    historical_text_blocks = ["RESPONSE_CODE_May26", "RESPONSE_CODE_Apr26", "RESPONSE_CODE_Mar26", "RESPONSE_CODE_Feb26", "RESPONSE_CODE_Jan26"]
    for col in historical_text_blocks:
        processed_df[col] = processed_df[col].fillna("OK")

    for col in MASTER_108_HEADERS:
        if processed_df[col].isna().all() or processed_df[col].isnull().all():
            if col in ["WRITEOFF_TAG", "NPA_TYPE", "MODULE", "FINAL_ALLO_ID", "RESPONSE_CODE_NEW"]:
                processed_df[col] = processed_df[col].fillna("STANDARD")
            elif "DATE" in col or "MAKEDATE" in col:
                processed_df[col] = processed_df[col].fillna("2024-06-15")
            else:
                processed_df[col] = processed_df[col].fillna(0)

    return processed_df

def compute_bucket_counts(df: pd.DataFrame) -> dict:
    """Calculates row counts across all 5 delinquency stages safely."""
    if df is None or df.empty:
        return {"b0": 0, "b1": 0, "b2": 0, "b3": 0, "b4": 0}
    bkt_series = df["LAN_BKT"].astype(str).str.strip()
    return {
        "b0": len(df[bkt_series == "0"]),
        "b1": len(df[bkt_series == "1"]),
        "b2": len(df[bkt_series == "2"]),
        "b3": len(df[bkt_series == "3"]),
        "b4": len(df[bkt_series == "4"]),
    }

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

    fig = px.pie(summary, values="EXPOSURE_POS", names=names_col, color=names_col, color_discrete_map=color_map, hole=0.4)
    fig.update_traces(textinfo="percent+label", textposition="outside", hovertemplate="<b>%{label}</b><br>Exposure: ₹%{value:,.0f}<br>% Share: %{percent}")
    fig.update_layout(title={"text": f"<b>{title}</b>", "y": 0.95, "x": 0.5, "xanchor": "center"}, showlegend=False, margin=dict(t=60, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig
def generate_audit_pdf(target_id: str, row_dict: dict) -> bytes:
    """Generates a professional executive-ready PDF audit report using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor("#1e3c72"), spaceAfter=15, alignment=1)
    section_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#2a5298"), spaceBefore=12, spaceAfter=6)
    cell_label_style = ParagraphStyle('CellLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#4a5568"))
    cell_value_style = ParagraphStyle('CellValue', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#1a202c"))
    alert_value_style = ParagraphStyle('AlertValue', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#c0392b"))

    story.append(Paragraph("CREDITPULSE AI — 108-HEADER COMPLIANCE AUDIT REPORT", title_style))
    story.append(Paragraph(f"<b>Account Identification Key:</b> {target_id}", cell_value_style))
    story.append(Spacer(1, 10))
    
    def safe_numeric_convert(val) -> int:
        if pd.isna(val) or str(val).strip() == '' or str(val).lower() == 'nan':
            return 0
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return 0

    def create_section_table(data_matrix):
        t = Table(data_matrix, colWidths=[140, 130, 140, 130])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        return t

    emi = safe_numeric_convert(row_dict.get('LOAN_EMI', 0))
    bkt = safe_numeric_convert(row_dict.get('LAN_BKT', 0))
    dpd = safe_numeric_convert(row_dict.get('LAN_DPD', 0))
    
    actual_overdue_principal = safe_numeric_convert(row_dict.get('LAN_INST_OV_AMT', 0))
    calculated_late_fees = safe_numeric_convert(row_dict.get('OVERDUE_CHARGE', 0))

    # Section 1
    story.append(Paragraph("1. Sourcing & Identification Parameters", section_style))
    sect1_data = [
        [Paragraph("Product Group (LAN_PDT):", cell_label_style), Paragraph(str(row_dict.get('LAN_PDT', '')), cell_value_style), Paragraph("Module Category:", cell_label_style), Paragraph(str(row_dict.get('MODULE', '')), cell_value_style)],
        [Paragraph("Customer Name:", cell_label_style), Paragraph(str(row_dict.get('CUSTOMERNAME', '')), cell_value_style), Paragraph("Loan Account No:", cell_label_style), Paragraph(str(row_dict.get('LOAN_NO', '')), cell_value_style)],
        [Paragraph("Original Disbursal Date:", cell_label_style), Paragraph(str(row_dict.get('DISB_DATE', '')), cell_value_style), Paragraph("Disbursed Principal:", cell_label_style), Paragraph(f"₹{safe_numeric_convert(row_dict.get('LAN_DISB_AMT', 0)):,}", cell_value_style)]
    ]
    story.append(create_section_table(sect1_data))
    
    # Section 2
    story.append(Paragraph("2. Collateral Asset Verification Parameters", section_style))
    doc_make, doc_model, doc_reg = str(row_dict.get('MAKE', '')), str(row_dict.get('MODEL', '')), str(row_dict.get('REGDNUM', ''))
    sect2_data = [
        [Paragraph("Make / Restructuring:", cell_label_style), Paragraph(doc_make if doc_make.strip() != "" and doc_make.lower() != 'nan' else "NONE", cell_value_style), Paragraph("Asset Model / Segment:", cell_label_style), Paragraph(doc_model if doc_model.strip() != "" and doc_model.lower() != 'nan' else "NONE", cell_value_style)],
        [Paragraph("Registration Refs (REGDNUM):", cell_label_style), Paragraph(doc_reg if doc_reg.strip() != "" and doc_reg.lower() != 'nan' else "NONE", cell_value_style), Paragraph("HL / LAP Flags:", cell_label_style), Paragraph(f"{row_dict.get('HL_NONHL','')} | {row_dict.get('LAP_NONLAP','')}", cell_value_style)]
    ]
    story.append(create_section_table(sect2_data))
    
    # Section 3
    story.append(Paragraph("3. Monthly Billing & Active Balances", section_style))
    sect3_data = [
        [Paragraph("Gateway Presentation Mode:", cell_label_style), Paragraph(str(row_dict.get('REPAY_MODE', '')), cell_value_style), Paragraph("Loan Scheduled EMI:", cell_label_style), Paragraph(f"₹{emi:,}", cell_value_style)],
        [Paragraph("Principal Bal (LAN_POS):", cell_label_style), Paragraph(f"₹{safe_numeric_convert(row_dict.get('LAN_POS', 0)):,}", cell_value_style), Paragraph("Total Exposure POS Risk:", cell_label_style), Paragraph(f"₹{safe_numeric_convert(row_dict.get('EXPOSURE_POS', 0)):,}", cell_value_style)]
    ]
    story.append(create_section_table(sect3_data))
    
    # Section 4
    story.append(Paragraph("4. Delinquency Buckets & Field Allocations", section_style))
    sect4_data = [
        [Paragraph("Days Past Due (LAN_DPD):", cell_label_style), Paragraph(f"{dpd} Days", alert_value_style), Paragraph("Risk Bucket:", cell_label_style), Paragraph(f"Bucket {bkt}", cell_value_style)],
        [Paragraph("Total Overdue Principal (Actual):", cell_label_style), Paragraph(f"₹{actual_overdue_principal:,}", cell_value_style), Paragraph("Late Presentation Fees (Calculated):", cell_label_style), Paragraph(f"₹{calculated_late_fees:,}", cell_value_style)],
        [Paragraph("Assigned Agency ID Desk:", cell_label_style), Paragraph(str(row_dict.get('FINAL_ALLO_ID', 'NA')), cell_value_style), Paragraph("Field Action Response Code:", cell_label_style), Paragraph(str(row_dict.get('RESPONSE_CODE_NEW', 'NA')), cell_value_style)],
        [Paragraph("NPA Status Code:", cell_label_style), Paragraph(str(row_dict.get('NPA_TYPE', 'NA')), cell_value_style), Paragraph("Account Writeoff Status:", cell_label_style), Paragraph(str(row_dict.get('WRITEOFF_TAG', 'NA')), cell_value_style)]
    ]
    story.append(create_section_table(sect4_data))
    
    # Section 5
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Official Mandated Playbook Strategy Directive", section_style))
    strategies = {
        0: "MONITORING LOG: Account is currently standard. Continue normal presentation drops.",
        1: "DIGITAL REMINDER INTERVENTION: Missed current cycle payment date (1-30 DPD). Deploy automated outreach pipelines via SMS, WhatsApp, and interactive voice response drops.",
        2: "TELE-CALLING ESCALATION: 31-60 DPD tier reach. Route directly to soft card tele-calling queues for balance configuration layout options.",
        3: "FIELD VISIT ENGAGEMENT: 61-90 DPD tier reach. Dispatch localized field collections team to arrange property visit profiles.",
        4: "LIQUIDATION PROCEEDINGS: Hard recovery NPA trigger. Route directly to liquidation desk asset auction workflow channels."
    }
    directive_text = strategies.get(bkt, "REVIEW OPERATIONAL LEDGER: Asset logic pools boundary out of spec.")
    story.append(Paragraph(directive_text, cell_value_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
