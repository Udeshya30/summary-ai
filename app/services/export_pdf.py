from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

def generate_pdf(summary_text, findings, risk_score, exposure):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Internal Audit Summary Report</b>", styles['Title']))
    elements.append(Spacer(1, 20))

    # Executive Summary
    elements.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
    elements.append(Paragraph(summary_text, styles['BodyText']))
    elements.append(Spacer(1, 20))

    # Risk + Exposure Blocks
    elements.append(Paragraph(f"<b>Total Risk Score:</b> {risk_score}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Total Financial Exposure:</b> ₹{exposure:,}", styles['BodyText']))
    elements.append(Spacer(1, 20))

    # Findings Table
    if findings:
        table_data = [["Issue", "Impact", "Risk", "Root Cause"]]

        for row in findings:
            table_data.append([
                row.get("issue"),
                row.get("impact"),
                row.get("risk"),
                row.get("root_cause"),
            ])

        table = Table(table_data, colWidths=[5*cm, 4*cm, 3*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.black),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ]))

        elements.append(Paragraph("<b>Audit Findings</b>", styles['Heading2']))
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
