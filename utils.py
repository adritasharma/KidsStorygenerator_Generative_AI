import os
import io
import base64
import shutil
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import textwrap

outputs_folder = "outputs"
if os.path.exists(outputs_folder):
    shutil.rmtree(outputs_folder)
os.makedirs(outputs_folder, exist_ok=True)

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
    """Export story text and scene images to a PDF."""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    margin = 40
    max_width = width - 2 * margin
    line_height = 16
    c.setFont("Helvetica", 12)

    y = height - 50

    # Wrap and draw story text
    for paragraph in story_text.split("\n"):
        lines = textwrap.wrap(paragraph, width=80)  # Wrap text to 80 chars
        for line in lines:
            if y < 50:  # Start new page if bottom reached
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 12)
            c.drawString(margin, y, line)
            y -= line_height

    # Add images for each scene
    for i in range(scene_count):
        img_path = f"outputs/scene_{i+1}.png"
        if os.path.exists(img_path):
            c.showPage()
            img = ImageReader(img_path)
            # Fit image width inside page with margin
            img_width = width - 2 * margin
            c.drawImage(img, margin, 150, width=img_width, preserveAspectRatio=True, mask='auto')
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin, 100, f"Scene {i+1}")

    c.save()
    return f"✅ Storybook exported to {output_path}!"
