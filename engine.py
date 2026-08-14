import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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

def generate_audit_pdf(target_id: str, row_dict: dict) -> bytes:
    """Generates a professional executive-ready PDF audit report using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20,
        textColor=colors.HexColor("#1e3c72"), spaceAfter=15, alignment=1
    )
    section_style = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12,
        textColor=colors.HexColor("#2a5298"), spaceBefore=12, spaceAfter=6
    )
    cell_label_style = ParagraphStyle(
        'CellLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#4a5568")
    )
    cell_value_style = ParagraphStyle(
        'CellValue', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#1a202c")
    )
    alert_value_style = ParagraphStyle(
        'AlertValue', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#c0392b")
    )

    story.append(Paragraph("CREDITPULSE AI — SYSTEM LEDGER AUDIT REPORT", title_style))
    story.append(Paragraph(f"<b>Account Identification Key:</b> {target_id}", cell_value_style))
    story.append(Spacer(1, 10))
    
    def create_section_table(data_matrix):
        t = Table(data_matrix, colWidths=)
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        return t

    story.append(Paragraph("1. Sourcing & Identification Parameters", section_style))
    sect1_data = [
        [Paragraph("Product Group (LAN_PDT):", cell_label_style), Paragraph(str(row_dict.get('LAN_PDT', ''))), cell_value_style),
         Paragraph("Module Category:", cell_label_style), Paragraph(str(row_dict.get('MODULE', ''))), cell_value_style)],
        [Paragraph("Customer Name:", cell_label_style), Paragraph(str(row_dict.get('CUSTOMERNAME', ''))), cell_value_style),
         Paragraph("Loan Account No:", cell_label_style), Paragraph(str(row_dict.get('LOAN_NO', ''))), cell_value_style)],
        [Paragraph("Original Disbursal Date:", cell_label_style), Paragraph(str(row_dict.get('DISB_DATE', ''))), cell_value_style),
         Paragraph("Disbursed Principal:", cell_label_style), Paragraph(f"₹{int(row_dict.get('LAN_DISB_AMT', 0)):,}", cell_value_style)]
    ]
    story.append(create_section_table(sect1_data))
    
    story.append(Paragraph("2. Collateral Asset Verification Parameters", section_style))
    sect2_data = [
        [Paragraph("Make / Restructuring:", cell_label_style), Paragraph(str(row_dict.get('MAKE', ''))), cell_value_style),
         Paragraph("Asset Model / Segment:", cell_label_style), Paragraph(str(row_dict.get('MODEL', ''))), cell_value_style)],
        [Paragraph("Registration Refs (REGDNUM):", cell_label_style), Paragraph(str(row_dict.get('REGDNUM', ''))), cell_value_style),
         Paragraph("HL / LAP Flags:", cell_label_style), Paragraph(f"{row_dict.get('HL_NONHL','')} | {row_dict.get('LAP_NONLAP','')}", cell_value_style)]
    ]
    story.append(create_section_table(sect2_data))
    
    story.append(Paragraph("3. Monthly Billing & Active Balances", section_style))
    sect3_data = [
        [Paragraph("Gateway Presentation Mode:", cell_label_style), Paragraph(str(row_dict.get('REPAY_MODE', ''))), cell_value_style),
         Paragraph("Loan Scheduled EMI:", cell_label_style), Paragraph(f"₹{int(row_dict.get('LOAN_EMI', 0)):,}", cell_value_style)],
        [Paragraph("Principal Bal (LAN_POS):", cell_label_style), Paragraph(f"₹{int(row_dict.get('LAN_POS', 0)):,}", cell_value_style),
         Paragraph("Total Exposure POS Risk:", cell_label_style), Paragraph(f"₹{int(row_dict.get('EXPOSURE_POS', 0)):,}", cell_value_style)]
    ]
    story.append(create_section_table(sect3_data))
    
    story.append(Paragraph("4. Delinquency Buckets & Field Allocations", section_style))
    sect4_data = [
        [Paragraph("Days Past Due (LAN_DPD):", cell_label_style), Paragraph(f"{row_dict.get('LAN_DPD', 0)} Days", alert_value_style),
         Paragraph("Risk Bucket:", cell_label_style), Paragraph(f"Bucket {row_dict.get('LAN_BKT', 0)}", cell_value_style)],
        [Paragraph("Total Overdue Principal:", cell_label_style), Paragraph(f"₹{int(row_dict.get('LAN_INST_OV_AMT', 0)):,}", cell_value_style),
         Paragraph("Late Presentation Fees:", cell_label_style), Paragraph(f"₹{int(row_dict.get('OVERDUE_CHARGE', 0)):,}", cell_value_style)],
        [Paragraph("Assigned Agency ID Desk:", cell_label_style), Paragraph(str(row_dict.get('FINAL_ALLO_ID', ''))), cell_value_style),
         Paragraph("Field Action Response:", cell_label_style), Paragraph(str(row_dict.get('RESPONSE_CODE_NEW', ''))), cell_value_style)],
        [Paragraph("NPA Status Code:", cell_label_style), Paragraph(str(row_dict.get('NPA_TYPE', ''))), cell_value_style),
         Paragraph("Account Writeoff Status:", cell_label_style), Paragraph(str(row_dict.get('WRITEOFF_TAG', ''))), cell_value_style)]
    ]
    story.append(create_section_table(sect4_data))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
