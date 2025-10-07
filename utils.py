from datetime import datetime
import os
import io
import base64
import shutil
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import textwrap
from reportlab.lib import colors
import os
import shutil
from datetime import datetime


def prepare_output_folder(base_folder="outputs"):
    """
    Ensures the output folder is ready for new files.
    If old files exist, moves them into a timestamped subfolder.
    """
    # Create base folder if not exists
    os.makedirs(base_folder, exist_ok=True)

    # If the folder is not empty, archive its contents
    if os.listdir(base_folder):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_subfolder = os.path.join(base_folder, f"old_{timestamp}")
        os.makedirs(archive_subfolder, exist_ok=True)

        # Move existing files/folders to archive subfolder
        for item in os.listdir(base_folder):
            src_path = os.path.join(base_folder, item)
            dst_path = os.path.join(archive_subfolder, item)
            if src_path != archive_subfolder:  # avoid recursive move
                shutil.move(src_path, dst_path)

        print(f"📦 Archived old files to: {archive_subfolder}")

    print(f"✅ Output folder ready: {base_folder}")

    return base_folder

def display_image(path):
    """Convert image to base64 for Dash display."""
    if not os.path.exists(path):
        return ""
    encoded = base64.b64encode(open(path, "rb").read()).decode()
    return f"data:image/png;base64,{encoded}"

def save_uploaded_image(contents):
    """Return PIL Image from uploaded Dash image contents."""
    if not contents:
        return None
    header, encoded = contents.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    img = img.resize((256, 256))
    return img


def export_story_to_pdf(story_text, scene_count, output_path="outputs/storybook.pdf"):
    """Export story text and scene images to a colorful kids-friendly PDF."""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    margin = 50
    max_width = width - 2 * margin
    y = height - 70

    # Fonts and colors
    title_font = "Helvetica-BoldOblique"
    story_font = "Helvetica"
    story_font_size = 14
    line_height = 20

    def draw_title(text):
        nonlocal y
        if y < 100:
            c.showPage()
            y = height - 70
        c.setFillColor(colors.lightblue)
        c.rect(margin - 10, y - 10, max_width + 20, 28, fill=True, stroke=False)
        c.setFillColor(colors.darkblue)
        c.setFont(title_font, 16)
        c.drawString(margin, y, text)
        y -= 40  # space after title

    def draw_paragraph(paragraph):
        nonlocal y
        c.setFont(story_font, story_font_size)
        c.setFillColor(colors.black)
        lines = textwrap.wrap(paragraph.strip(), width=75)
        for line in lines:
            if y < 60:
                c.showPage()
                y = height - 70
                c.setFont(story_font, story_font_size)
            c.drawString(margin, y, line)
            y -= line_height
        y -= 10  # gap between paragraphs

    # Split text into titled sections
    paragraphs = story_text.strip().split("\n")
    for p in paragraphs:
        if not p.strip():
            continue
        if p.strip().endswith("Shiny") or "Tries" in p or "Truth" in p:  # Title detection
            draw_title(p.strip())
        else:
            draw_paragraph(p.strip())

    # Add a little heart separator
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.pink)
    c.drawCentredString(width / 2, y - 10, "❤️ ❤️ ❤️")
    y -= 30

    # Add scene images
    for i in range(scene_count):
        img_path = f"outputs/scene_{i+1}.png"
        if os.path.exists(img_path):
            c.showPage()
            c.setFillColor(colors.orange)
            c.rect(0, height - 70, width, 40, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2, height - 55, f"Scene {i + 1}")

            img = ImageReader(img_path)
            img_width = width - 2 * margin
            c.drawImage(img, margin, 150, width=img_width, preserveAspectRatio=True, mask='auto')

    c.save()
    return f"✅ Storybook exported to {output_path}!"