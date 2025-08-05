import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from django.http import HttpResponse
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generate_invoice_pdf(order):
    """
    Generate professional single-page PDF invoice with proper currency symbol handling
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=0.5*inch, 
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles with proper font handling
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=5,
        alignment=0,  # Left alignment
        textColor=colors.HexColor('#1e40af'),
        fontName='Helvetica-Bold'
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=10,
        alignment=2,  # Right alignment
        textColor=colors.HexColor('#dc2626'),
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        fontName='Helvetica'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#374151')
    )
    
    # Calculate total cost
    total_cost = order.get_total_cost()
    
    # Create header table with company info and invoice details
    header_data = [
        [
            Paragraph('<b>Bell Server</b><br/>Premium VPS Hosting Solutions<br/><br/>Bell Server Pvt Ltd<br/>123 Tech Park, Digital City<br/>Bengaluru, Karnataka 560001<br/>India<br/><br/>Email: info@bellserver.com<br/>Phone: +91-XXX-XXX-XXXX<br/>Website: www.bellserver.com<br/>GST: 29XXXXX1234X1ZX', section_style),
            Paragraph(f'<b>INVOICE</b><br/>Invoice #: BS-{order.id:05d}<br/>Date: {order.created.strftime("%B %d, %Y")}<br/>Status: <font color="green"><b>PAID</b></font><br/><br/><b>Payment Details:</b><br/>Method: Razorpay (Online)<br/>Order ID: {order.razorpay_order_id or "N/A"}<br/>Payment ID: {order.razorpay_payment_id or "N/A"}<br/>Date: {order.created.strftime("%B %d, %Y")}', invoice_title_style)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    
    elements.append(header_table)
    
    # Add a line separator
    line_data = [['', '']]
    line_table = Table(line_data, colWidths=[7*inch])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(line_table)
    
    # Billing information
    elements.append(Paragraph('<b>BILL TO:</b>', header_style))
    billing_info = f"""
    {order.first_name} {order.last_name}<br/>
    {order.email}<br/>
    {order.address}<br/>
    {order.city}, {order.state} {order.postal_code}<br/>
    Phone: {order.phone}
    """
    elements.append(Paragraph(billing_info, section_style))
    elements.append(Spacer(1, 15))
    
    # Order items table
    elements.append(Paragraph('<b>ORDER DETAILS:</b>', header_style))
    
    # Table header
    data = [
        ['Service Description', 'Duration', 'Quantity', 'Unit Price', 'Total Amount']
    ]
    
    # Add order items
    for item in order.items.all():
        unit_price = f"₹{item.price:,.0f}"
        total_amount = f"₹{item.get_cost():,.0f}"
        
        data.append([
            item.plan.name,
            item.plan.get_duration_display(),
            str(item.quantity),
            unit_price,
            total_amount
        ])
    
    # Add subtotal and total rows
    data.extend([
        ['', '', '', '', ''],  # Empty row for spacing
        ['', '', '', 'Subtotal:', f'₹{total_cost:,.0f}'],
        ['', '', '', 'Tax (0%):', '₹0'],
        ['', '', '', 'TOTAL:', f'₹{total_cost:,.0f}']
    ])
    
    # Create table
    table = Table(data, colWidths=[2.8*inch, 1*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -4), 9),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -4), [colors.white, colors.HexColor('#f9fafb')]),
        
        # Total section
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -3), (-1, -1), 10),
        ('ALIGN', (3, -3), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1f2937')),
        
        # Grid lines
        ('GRID', (0, 0), (-1, -4), 1, colors.HexColor('#e5e7eb')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e40af')),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor('#d1d5db')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#374151')),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Service information in a compact format
    service_terms_data = [
        [
            Paragraph('<b>Service Information:</b><br/>• VPS servers provisioned within 2-4 hours<br/>• Access credentials sent via email within 24 hours<br/>• 24/7 technical support included<br/>• Free server monitoring and basic security setup<br/>• Annual billing cycle begins upon server activation', section_style),
            Paragraph('<b>Terms & Conditions:</b><br/>• Payment is non-refundable after service activation<br/>• Annual charges will be auto-debited from your account<br/>• 99.9% uptime guarantee with SLA protection<br/>• Fair usage policy applies to all services<br/>• For support, contact: support@bellserver.com', section_style)
        ]
    ]
    
    service_table = Table(service_terms_data, colWidths=[3.5*inch, 3.5*inch])
    service_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(service_table)
    
    # Footer
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#6b7280'),
        spaceBefore=15
    )
    
    footer_text = """
    <b>Thank you for choosing Bell Server!</b><br/>
    For any queries regarding this invoice, please contact our support team.<br/>
    Email: support@bellserver.com | Phone: +91-XXX-XXX-XXXX | Website: www.bellserver.com
    """
    
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def send_invoice_email(order):
    """
    Send invoice email with PDF attachment to customer
    """
    from django.core.mail import EmailMessage
    from django.template.loader import render_to_string
    from django.contrib.staticfiles.storage import staticfiles_storage

    try:
        # Generate PDF invoice
        pdf_content = generate_invoice_pdf(order)

        # Build absolute URL for logo (adjust domain for production)
        # For production, use something like: site_domain = 'https://www.bellserver.com'
        site_domain = 'http://127.0.0.1:8000' 
        logo_url = site_domain + staticfiles_storage.url('images/icon.png')

        # Render email template
        email_html = render_to_string('serverproject/emails/invoice_email.html', {
            'order': order,
            'customer_name': f"{order.first_name} {order.last_name}",
            'logo_url': logo_url
        })

        # Create email
        subject = f' Bell Server Invoice #{order.id:05d} - Payment Confirmed!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [order.email]
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=email_html,
            from_email=from_email,
            to=to_email,
        )
        
        # Set content type to HTML
        email.content_subtype = 'html'
        
        # Attach PDF invoice
        email.attach(
            filename=f'Bell_Server_Invoice_{order.id:06d}.pdf',
            content=pdf_content,
            mimetype='application/pdf'
        )
        
        # Send email
        email.send()
        return True
        
    except Exception as e:
        # Log error (you might want to use proper logging)
        print(f"Error sending invoice email: {e}")
        return False
