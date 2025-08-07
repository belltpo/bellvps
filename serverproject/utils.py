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
import logging
import urllib.request

# Get an instance of a logger
logger = logging.getLogger(__name__)

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

    # Register a font that supports the Rupee symbol
    try:
        # Assuming a 'fonts' directory exists in your static files
        font_path = os.path.join(settings.STATIC_ROOT or os.path.join(settings.BASE_DIR, 'serverproject', 'static'), 'fonts', 'DejaVuSans.ttf')
        if not os.path.exists(font_path):
             # Fallback for development when STATIC_ROOT might not be collected
            font_path = os.path.join(settings.BASE_DIR, 'serverproject', 'static', 'fonts', 'DejaVuSans.ttf')
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        main_font = 'DejaVuSans'
    except Exception as e:
        logger.warning(f"Could not register 'DejaVuSans' font, falling back to Helvetica. Rupee symbol may not render. Error: {e}")
        main_font = 'Helvetica' # Fallback font

    # Custom styles for a professional look
    try:
        logo_url = 'https://www.bellglobal.in/wp-content/uploads/2021/02/New-Logo-BellGlobal.png'
        with urllib.request.urlopen(logo_url) as url:
            logo_data = url.read()
        logo = Image(io.BytesIO(logo_data), width=1.4*inch, height=0.4*inch) # Adjusted for rectangular logo
    except Exception as e:
        logger.error(f"Failed to download logo for PDF, using text fallback: {e}")
        logo = Paragraph('BellGlobal', ParagraphStyle('CompanyStyle', parent=styles['h1'], fontSize=18, leading=22, textColor=colors.HexColor('#111827'), fontName=main_font)) # Fallback to text if image fails

    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['h1'],
        fontName=main_font,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#111827'),
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitleStyle',
        parent=styles['h1'],
        fontName=main_font,
        fontSize=28,
        textColor=colors.HexColor('#374151'),
        alignment=2 # Right alignment
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4b5563')
    )

    # --- Header Section ---
    header_data = [
        [logo, '', Paragraph('INVOICE', invoice_title_style)]
    ]
    header_table = Table(header_data, colWidths=[2*inch, 3*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(header_table)

    # --- Invoice Details ---
    invoice_details_data = [
        ['', Paragraph(f'<b>Invoice #</b>: BS-{order.id:05d}<br/><b>Date</b>: {order.created.strftime("%B %d, %Y")}', section_style)]
    ]
    invoice_details_table = Table(invoice_details_data, colWidths=[4.5*inch, 2.5*inch])
    invoice_details_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(invoice_details_table)

    # Add a line separator
    line = Table([['', '']], colWidths=[7*inch], rowHeights=[2])
    line.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(line)

    # --- Billing and Company Info ---
    billing_address = f"""
        {order.billing_name or f'{order.first_name} {order.last_name}'}<br/>
        {order.billing_address or order.address}<br/>
        {order.billing_city or order.city}, {order.billing_state or order.state} {order.billing_postal_code or order.postal_code}<br/>
        <br/>
        <b>Email:</b> {order.email}<br/>
        <b>Phone:</b> {order.phone}<br/>
        <b>Broker:</b> {order.get_broker_name_display()}
    """

    company_address = f"""
        <b>BellGlobal</b><br/>
        406, Ground Floor, 80 Feet Road,<br/>
        R.K. Layout, Padmanabhnagar,<br/>
        Bengaluru, KA, 560070<br/>
        India<br/>
        <br/>
        <b>Email:</b> helpdesk@bellglobal.in<br/>
        <b>Website:</b> www.bellglobal.in<br/>
        <b>GSTIN:</b> 29XXXXX1234X1ZX
    """

    address_data = [
        [Paragraph('<b>Bill To:</b>', header_style), Paragraph('<b>From:</b>', header_style)],
        [Paragraph(billing_address, section_style), Paragraph(company_address, section_style)]
    ]
    address_table = Table(address_data, colWidths=[3.5*inch, 3.5*inch])
    address_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(address_table)

    # --- Order Items Table ---
    items_data = [['#', 'Service Description', 'Unit Price', 'Total']]
    for i, item in enumerate(order.items.all()):
        item_price = f'₹{item.price:,.2f}'
        item_total = f'₹{item.get_cost():,.2f}'
        items_data.append([
            str(i + 1),
            Paragraph(f"<b>{item.plan.name}</b><br/><font size='9' color='#6b7280'>Annual Plan</font>", section_style),
            item_price,
            item_total
        ])

    table = Table(items_data, colWidths=[0.4*inch, 4.1*inch, 1.25*inch, 1.25*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), main_font), # Use the registered font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    elements.append(table)

    # --- Totals Section ---
    total_cost = order.get_total_cost()
    totals_data = [
        ['Subtotal', f'₹{total_cost:,.2f}'],
        ['Tax (0%)', '₹0.00'],
        [Paragraph('<b>Total Amount</b>', section_style), 
         Paragraph(f'<b>₹{total_cost:,.2f}</b>', section_style)]
    ]
    totals_table = Table(totals_data, colWidths=[5.5*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), main_font), # Use the registered font
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 2), (-1, 2), 10),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))

    # --- Payment Information ---
    payment_info = f"""
        <b>Payment Status:</b> <font color="green">PAID</font><br/>
        <b>Payment Method:</b> Razorpay (Online)<br/>
        <b>Order ID:</b> {order.razorpay_order_id or 'N/A'}<br/>
        <b>Payment ID:</b> {order.razorpay_payment_id or 'N/A'}
    """
    elements.append(Paragraph('<b>Payment Details</b>', header_style))
    elements.append(Paragraph(payment_info, section_style))
    elements.append(Spacer(1, 30))

    # --- Footer ---
    footer_text = """
        <b>Thank you for your business!</b><br/>
        <font size="9" color="#6b7280">If you have any questions, please contact support at support@bellserver.com.</font>
    """
    elements.append(Paragraph(footer_text, ParagraphStyle('FooterStyle', parent=styles['Normal'], alignment=1, textColor=colors.HexColor('#374151'))))

    doc.build(elements)
    
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
        logo_url = site_domain + staticfiles_storage.url('serverproject/images/icon.png')

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
        logger.info(f"Successfully sent invoice email for order {order.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending invoice email for order {order.id}: {e}", exc_info=True)
        return False
