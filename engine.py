from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_audit_pdf(target_id: str, row_dict: dict) -> bytes:
    """Generates a professional executive-ready PDF audit report using ReportLab."""
    buffer = BytesIO()
    
    # 1. Initialize Document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    story = []
    
    # 2. Styles Definition
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor("#1e3c72"),
        spaceAfter=15,
        alignment=1 # Centered
    )
    
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#2a5298"),
        spaceBefore=15,
        spaceAfter=6,
        borderPadding=2
    )
    
    cell_label_style = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor("#4a5568")
    )
    
    cell_value_style = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#1a202c")
    )

    alert_value_style = ParagraphStyle(
        'AlertValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor("#c0392b")
    )

    # 3. Document Header Banner
    story.append(Paragraph(f"CREDITPULSE AI — SYSTEM LEDGER AUDIT REPORT", title_style))
    story.append(Paragraph(f"<b>Account Identification Key:</b> {target_id}", cell_value_style))
    story.append(Spacer(1, 10))
    
    # 4. Table Construction Helper
    def create_section_table(data_matrix):
        t = Table(data_matrix, colWidths=[150, 120, 130, 130])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        return t

    # --- SECTION 1: Sourcing & Identification ---
    story.append(Paragraph("1. Sourcing & Identification Parameters", section_style))
    sect1_data = [
        [Paragraph("Product Group (LAN_PDT):", cell_label_style), Paragraph(str(row_dict.get('LAN_PDT', '')), cell_value_style),
         Paragraph("Module Category:", cell_label_style), Paragraph(str(row_dict.get('MODULE', '')), cell_value_style)],
        [Paragraph("Customer Name:", cell_label_style), Paragraph(str(row_dict.get('CUSTOMERNAME', '')), cell_value_style),
         Paragraph("Loan Account No:", cell_label_style), Paragraph(str(row_dict.get('LOAN_NO', '')), cell_value_style)],
        [Paragraph("Original Disbursal Date:", cell_label_style), Paragraph(str(row_dict.get('DISB_DATE', '')), cell_value_style),
         Paragraph("Disbursed Principal:", cell_label_style), Paragraph(f"₹{int(row_dict.get('LAN_DISB_AMT', 0)):,}", cell_value_style)]
    ]
    story.append(create_section_table(sect1_data))
    
    # --- SECTION 2: Collateral Asset Verification ---
    story.append(Paragraph("2. Collateral Asset Verification Parameters", section_style))
    sect2_data = [
        [Paragraph("Make / Restructuring:", cell_label_style), Paragraph(str(row_dict.get('MAKE', '')), cell_value_style),
         Paragraph("Asset Model / Segment:", cell_label_style), Paragraph(str(row_dict.get('MODEL', '')), cell_value_style)],
        [Paragraph("Registration Refs (REGDNUM):", cell_label_style), Paragraph(str(row_dict.get('REGDNUM', '')), cell_value_style),
         Paragraph("HL / LAP Flags:", cell_label_style), Paragraph(f"{row_dict.get('HL_NONHL','')} | {row_dict.get('LAP_NONLAP','')}", cell_value_style)]
    ]
    story.append(create_section_table(sect2_data))
    
    # --- SECTION 3: Monthly Billing & Balances ---
    story.append(Paragraph("3. Monthly Billing & Active Balances", section_style))
    sect3_data = [
        [Paragraph("Gateway Presentation Mode:", cell_label_style), Paragraph(str(row_dict.get('REPAY_MODE', '')), cell_value_style),
         Paragraph("Loan Scheduled EMI:", cell_label_style), Paragraph(f"₹{int(row_dict.get('LOAN_EMI', 0)):,}", cell_value_style)],
        [Paragraph("Principal Bal (LAN_POS):", cell_label_style), Paragraph(f"₹{int(row_dict.get('LAN_POS', 0)):,}", cell_value_style),
         Paragraph("Total Exposure POS Risk:", cell_label_style), Paragraph(f"₹{int(row_dict.get('EXPOSURE_POS', 0)):,}", cell_value_style)]
    ]
    story.append(create_section_table(sect3_data))
    
    # --- SECTION 4: Delinquency Buckets & Field Allocations ---
    story.append(Paragraph("4. Delinquency Buckets & Field Allocations", section_style))
    sect4_data = [
        [Paragraph("Days Past Due (LAN_DPD):", cell_label_style), Paragraph(f"{row_dict.get('LAN_DPD', 0)} Days", alert_value_style),
         Paragraph("Risk Bucket:", cell_label_style), Paragraph(f"Bucket {row_dict.get('LAN_BKT', 0)}", cell_value_style)],
        [Paragraph("Total Overdue Principal:", cell_label_style), Paragraph(f"₹{int(row_dict.get('LAN_INST_OV_AMT', 0)):,}", cell_value_style),
         Paragraph("Late Presentation Fees:", cell_label_style), Paragraph(f"₹{int(row_dict.get('OVERDUE_CHARGE', 0)):,}", cell_value_style)],
        [Paragraph("Assigned Agency ID Desk:", cell_label_style), Paragraph(str(row_dict.get('FINAL_ALLO_ID', '')), cell_value_style),
         Paragraph("Field Action Response:", cell_label_style), Paragraph(str(row_dict.get('RESPONSE_CODE_NEW', '')), cell_value_style)],
        [Paragraph("NPA Status Code:", cell_label_style), Paragraph(str(row_dict.get('NPA_TYPE', '')), cell_value_style),
         Paragraph("Account Writeoff Status:", cell_label_style), Paragraph(str(row_dict.get('WRITEOFF_TAG', '')), cell_value_style)]
    ]
    story.append(create_section_table(sect4_data))
    
    # 5. Build and Return Byte Stream Data
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
