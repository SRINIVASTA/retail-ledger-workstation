# reports/pdf_factory.py
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class DocumentAuditFactory:
    """Generates official compliance PDF structures from customer profile details."""

    @staticmethod
    def generate_audit_pdf(target_id: str, row_dict: dict, allocation_strategy: str) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor("#1e3c72"), spaceAfter=12, alignment=1)
        section_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#2a5298"), spaceBefore=8, spaceAfter=4)
        cell_label_style = ParagraphStyle('CellLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#4a5568"))
        cell_value_style = ParagraphStyle('CellValue', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#1a202c"))
        strategy_style = ParagraphStyle('StrategyText', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=colors.HexColor("#2d3748"))

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
        
        risk_tiers = {
            0: "STANDARD / PERFORMING ASSET", 1: "SMA-0 / SPECIAL MENTION ACCOUNT",
            2: "SMA-1 / EARLY WARNING SUBSET", 3: "SMA-2 / HIGH RISK OUTLIER",
            4: "NPA / NON-PERFORMING SUBSTANDARD"
        }
        current_tier = risk_tiers.get(bkt, "NPA / NON-PERFORMING SUBSTANDARD")

        story.append(Paragraph("1. Risk Regulatory Status Metrics", section_style))
        meta_data = [
            [Paragraph("Regulatory Bucket Code:", cell_label_style), Paragraph(f"BUCKET_{bkt}", cell_value_style), Paragraph("Portfolio Risk Tier:", cell_label_style), Paragraph(current_tier, cell_value_style)],
            [Paragraph("Product Group (LAN_PDT):", cell_label_style), Paragraph(str(row_dict.get('LAN_PDT')), cell_value_style), Paragraph("Module Category:", cell_label_style), Paragraph(str(row_dict.get('MODULE', 'RETAIL')), cell_value_style)],
            [Paragraph("Customer Name:", cell_label_style), Paragraph(str(row_dict.get('CUSTOMERNAME')), cell_value_style), Paragraph("Loan Account No:", cell_label_style), Paragraph(str(row_dict.get('LOAN_NO')), cell_value_style)],
            [Paragraph("Original Disbursal Date:", cell_label_style), Paragraph(str(row_dict.get('DISB_DATE')), cell_value_style), Paragraph("Calculated Tenure:", cell_label_style), Paragraph(f"{vintage} Months Active", cell_value_style)],
            [Paragraph("Branch Facility Name:", cell_label_style), Paragraph(str(row_dict.get('BRANCH_DESC', 'NONE')), cell_value_style), Paragraph("Core Banking Sol ID:", cell_label_style), Paragraph(str(row_dict.get('SOLID', 'NONE')), cell_value_style)]
        ]
        t1 = Table(meta_data, colWidths=[130, 130, 130, 140])
        t1.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0"))]))
        story.append(t1)
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("2. Financial Balances & Field Allocations", section_style))
        sect_data = [
            [Paragraph("Original Disbursed Amount:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('LAN_DISB_AMT', 0)):,}", cell_value_style), Paragraph("Live Computed Balance (POS):", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('LAN_POS', 0)):,}", cell_value_style)],
            [Paragraph("Contractual Scheduled EMI:", cell_label_style), Paragraph(f"₹{emi:,}", cell_value_style), Paragraph("Total Exposure POS Risk:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('EXPOSURE_POS', 0)):,}", cell_value_style)],
            [Paragraph("Days Past Due (LAN_DPD):", cell_label_style), Paragraph(f"{dpd} Days", cell_value_style), Paragraph("Total Overdue Principal:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('LAN_INST_OV_AMT', 0)):,}", cell_value_style)],
            [Paragraph("Field Action Response Code:", cell_label_style), Paragraph(f"<b>{row_dict.get('RESPONSE_CODE_NEW','PAID')}</b>", cell_value_style), Paragraph("Late Presentation Fees:", cell_label_style), Paragraph(f"₹{safe_convert(row_dict.get('OVERDUE_CHARGE', 0)):,}", cell_value_style)]
        ]
        t2 = Table(sect_data, colWidths=[130, 130, 130, 140])
        t2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0"))]))
        story.append(t2)
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("3. Official Mandated Playbook Strategy Directive", section_style))
        story.append(Paragraph(str(allocation_strategy), strategy_style))
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
