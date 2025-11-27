"""
PDF Report Generator for GARCH Trading Bot
Generates professional PDF reports with GARCH analysis and AI insights
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


def create_pdf_report(report_data, filename=None):
    """
    Generate a PDF report from GARCH analysis data
    
    Args:
        report_data (dict): Dictionary containing:
            - title (str): Report title
            - timestamp (str): Report timestamp
            - price (float): Current BTC price
            - volatility (float): Predicted volatility
            - signal (str): Trading signal (BUY/SELL/HOLD)
            - ai_analysis (str): AI-generated analysis text
            - stats (dict): Additional statistics
        filename (str): Optional filename for the PDF
    
    Returns:
        bytes: PDF content as bytes
    """
    # Create a BytesIO buffer
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT,
        spaceAfter=10,
    )
    
    # Title
    title = Paragraph(report_data.get('title', 'GARCH Trading Bot Report'), title_style)
    elements.append(title)
    
    # Subtitle with timestamp
    timestamp = report_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    subtitle = Paragraph(f"<i>Generated: {timestamp}</i>", body_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary Section
    elements.append(Paragraph("📊 Market Summary", heading_style))
    
    # Summary Table
    summary_data = [
        ['Metric', 'Value'],
        ['Current BTC Price', f"${report_data.get('price', 0):,.2f}"],
        ['Predicted Volatility', f"{report_data.get('volatility', 0):.4f}%"],
        ['Trading Signal', report_data.get('signal', 'N/A')],
    ]
    
    # Add signal indicator color
    signal = report_data.get('signal', 'HOLD')
    signal_color = colors.HexColor('#27ae60') if signal == 'BUY' else \
                   colors.HexColor('#e74c3c') if signal == 'SELL' else \
                   colors.HexColor('#f39c12')
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TEXTCOLOR', (1, 3), (1, 3), signal_color),  # Signal row color
        ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # AI Analysis Section
    elements.append(Paragraph("🤖 AI Analysis", heading_style))
    
    ai_text = report_data.get('ai_analysis', 'No analysis available')
    # Process AI text to handle markdown-style formatting
    ai_paragraphs = ai_text.split('\n\n')
    for para in ai_paragraphs:
        if para.strip():
            elements.append(Paragraph(para.strip(), body_style))
            elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Additional Statistics (if available)
    if 'stats' in report_data and report_data['stats']:
        elements.append(Paragraph("📈 Additional Statistics", heading_style))
        
        stats = report_data['stats']
        stats_data = [['Statistic', 'Value']]
        
        for key, value in stats.items():
            if isinstance(value, float):
                stats_data.append([key.replace('_', ' ').title(), f"{value:.4f}"])
            else:
                stats_data.append([key.replace('_', ' ').title(), str(value)])
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(stats_table)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    footer_text = "<i>This report is for educational purposes only. Not financial advice.</i>"
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


if __name__ == "__main__":
    # Test PDF generation
    test_data = {
        'title': 'GARCH Trading Bot - Test Report',
        'timestamp': '2025-11-26 01:10:00',
        'price': 87500.50,
        'volatility': 0.4567,
        'signal': 'BUY',
        'ai_analysis': 'El mercado de Bitcoin muestra una volatilidad moderada. '
                       'La persistencia del modelo GARCH indica estabilidad a corto plazo.\\n\\n'
                       'Recomendación: Mantener posiciones actuales.',
        'stats': {
            'avg_volatility': 0.4500,
            'max_price': 88000.00,
            'min_price': 87000.00,
            'num_predictions': 150
        }
    }
    
    pdf_bytes = create_pdf_report(test_data, 'test_report.pdf')
    
    # Save test PDF
    with open('test_report.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
