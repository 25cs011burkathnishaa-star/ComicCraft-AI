import os
from datetime import datetime
from fpdf import FPDF

EXPORT_FOLDER = "static/exports"
FONT_PATH = "static/fonts/DejaVuSans.ttf"

def save_pdf(layout):
    """
    Compiles the full comic into a multi-page PDF file using the FPDF library.
    """
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    has_custom_font = os.path.exists(FONT_PATH)
    if has_custom_font:
        pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
        pdf.set_font('DejaVu', '', 12)
    else:
        pdf.set_font('Arial', '', 12)

    for panel in layout:
        image_path = panel['image_path']
        story_text = panel['text']
        
        pdf.add_page()
        
        if has_custom_font:
            pdf.set_font('DejaVu', '', 14)
        else:
            pdf.set_font('Arial', 'B', 14)
            
        pdf.cell(0, 10, f"Panel {panel['panel']}: {panel['title']}", 0, 1, align="C")
        
        if has_custom_font:
            pdf.set_font('DejaVu', '', 12)
        else:
            pdf.set_font('Arial', '', 12)
        
        y_image = 30
        image_height = 90
        spacing_after_image = 10
        
        if os.path.exists(image_path):
            try:
                pdf.image(image_path, x=20, y=y_image, w=pdf.w - 40, h=image_height)
            except Exception as e:
                pdf.set_y(y_image)
                pdf.multi_cell(0, 10, f"Image error: {str(e)}")
        else:
            pdf.set_y(y_image)
            pdf.multi_cell(0, 10, f"Image missing: {image_path}")
            
        pdf.set_y(y_image + image_height + spacing_after_image)
        pdf.multi_cell(0, 8, story_text)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(pdf_path)
    return pdf_path