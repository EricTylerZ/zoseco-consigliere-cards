from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import os
import tempfile
import datetime
import csv

# Register Century Schoolbook font (adjust path if needed)
try:
    pdfmetrics.registerFont(TTFont("CenturySchoolbook", "C:/Windows/Fonts/CENSCBK.TTF"))
    FONT_NAME = "CenturySchoolbook"
except:
    FONT_NAME = "Helvetica"

# Define color #00918b
royal_turquoise = Color(0, 0.569, 0.545)

# Card and page dimensions
CARD_WIDTH, CARD_HEIGHT = 3.5 * inch, 2 * inch
PAGE_WIDTH, PAGE_HEIGHT = letter

# Layout parameters
spacing = 0  # No spacing between columns
top_margin = 0.25 * inch
left_margin = (PAGE_WIDTH - (2 * CARD_WIDTH)) / 2  # Adjusted for no spacing

# Cards per page: 2 columns, 5 rows
cols, rows = 2, 5
total_cards = 10  # 1 page for testing

# Card content
name = "Eric Zosso"
title = "Tech Consigliere for humble owners"
description = "helping you take care of (pretty much) any problem"
services = "Rewards Programs, AI integration, AI to organize all your files, easy liability waivers, bitcoin/crypto integration"
contact = "(219) 241-3354  eric@zoseco.com"
address = "2175 S. Lafayette St, Denver, CO 80210"
base_url = "https://zoseco.com/tech-consigliere?card="

def wrap_text(text, width, font, font_size, c, centered=False):
    c.setFont(font, font_size)
    words = text.split()
    lines = []
    current_line = []
    current_width = 0
    for word in words:
        word_width = c.stringWidth(word + " ", font, font_size)
        if current_width + word_width <= width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_width = word_width
    if current_line:
        lines.append(" ".join(current_line))
    if centered:
        return [(line, c.stringWidth(line, font, font_size)) for line in lines]
    return lines

def create_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name)
    return temp_file.name

def draw_card(c, x, y, card_id, qr_code_url):
    c.setStrokeColor(royal_turquoise)
    c.setLineWidth(2)  # Thicker lines for easier cutting
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    
    margin = 0.125 * inch
    text_x = x + margin
    text_width = CARD_WIDTH - 2 * margin
    current_y = y + CARD_HEIGHT - margin
    
    # Name
    c.setFont(FONT_NAME, 12)
    c.setFillColor(royal_turquoise)
    name_width = c.stringWidth(name, FONT_NAME, 12)
    c.drawString(text_x + (text_width - name_width) / 2, current_y - 12, name)
    current_y -= 14
    
    # Title
    c.setFont(FONT_NAME, 10)
    wrapped_title = wrap_text(title, text_width, FONT_NAME, 10, c, centered=True)
    for line, line_width in wrapped_title:
        c.drawString(text_x + (text_width - line_width) / 2, current_y - 10, line)
        current_y -= 12
    
    # Description
    c.setFont(FONT_NAME, 8)
    c.setFillColorRGB(0, 0, 0)
    wrapped_desc = wrap_text(description, text_width, FONT_NAME, 8, c, centered=True)
    for line, line_width in wrapped_desc:
        c.drawString(text_x + (text_width - line_width) / 2, current_y - 8, line)
        current_y -= 10
    
    # Services
    c.setFont(FONT_NAME, 7)
    services_text = "Services: " + services
    wrapped_services = wrap_text(services_text, text_width, FONT_NAME, 7, c)
    for line in wrapped_services:
        c.drawString(text_x, current_y - 7, line)
        current_y -= 9
    
    # Bottom section with extra space
    bottom_y = y + margin
    qr_size = 1 * inch
    qr_x = x + CARD_WIDTH - margin - qr_size
    qr_y = bottom_y
    qr_file = create_qr_code(qr_code_url)
    c.drawImage(qr_file, qr_x, qr_y, qr_size, qr_size)
    os.remove(qr_file)
    
    # Contact and address with extra line break (pushed down)
    contact_x = text_x
    contact_y = bottom_y + qr_size - 30  # Adjusted to push down by extra line break
    c.setFont(FONT_NAME, 7)
    c.drawString(contact_x, contact_y, contact)
    c.drawString(contact_x, contact_y - 10, address)

def create_pdf():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"Eric_Zosso_Business_Cards_{timestamp}.pdf"
    csv_filename = "Zoseco_Business_Card_Tracker.csv"
    
    # Determine starting card number from existing CSV
    if os.path.isfile(csv_filename):
        with open(csv_filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            card_numbers = [int(row[1]) for row in reader if row]
            start_card_number = max(card_numbers) + 1 if card_numbers else 1
    else:
        start_card_number = 1
    
    # Generate card IDs
    card_ids = range(start_card_number, start_card_number + total_cards)
    
    # Write to CSV
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Name", "Card Number", "QR Code URL"])
        for card_id in card_ids:
            qr_code_url = f"{base_url}{card_id:03d}"
            writer.writerow(["Eric Zosso", card_id, qr_code_url])
    
    # Generate PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setTitle("Eric Zosso - Tech Consigliere Business Cards")
    c.setAuthor("Eric Zosso")
    c.setSubject("Business Cards for Eric Zosso")
    
    y_start = PAGE_HEIGHT - top_margin - CARD_HEIGHT
    y_positions = [y_start - i * (CARD_HEIGHT + spacing) for i in range(rows)]
    x_positions = [left_margin + j * CARD_WIDTH for j in range(cols)]  # No spacing
    
    for i, card_id in enumerate(card_ids):
        row = i // cols
        col = i % cols
        if row >= rows:
            break
        x = x_positions[col]
        y = y_positions[row]
        qr_code_url = f"{base_url}{card_id:03d}"
        draw_card(c, x, y, card_id, qr_code_url)
    
    c.save()
    print(f"PDF generated: {pdf_filename}")
    print(f"Added cards {start_card_number} to {start_card_number + total_cards - 1} to {csv_filename}")

if __name__ == "__main__":
    create_pdf()