"""
exporters.py
Compiles the complete comic (panels with images and narration) into a
professionally formatted multi-page PDF using FPDF.
"""

import os
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

from fpdf import FPDF

from app.config import EXPORTS_DIR

logger = logging.getLogger(__name__)

Path(EXPORTS_DIR).mkdir(parents=True, exist_ok=True)


def _clean_text(text: str) -> str:
    """Clean text for FPDF compatibility (convert/remove non-latin-1 characters)."""
    if not text:
        return ""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2014": "-", "\u2013": "-",
        "\u2026": "...", "\u2022": "-",
        "⚡": "", "📖": "", "🦸": "", "🌍": "", "🎭": "", "🎨": "",
        "📍": "", "💬": "", "•": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


class ComicPDF(FPDF):
    """Custom FPDF subclass for ComicCraft PDF generation."""

    def __init__(self, title: str = "ComicCraft - AI Generated Comic"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.comic_title = _clean_text(title)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """Custom header with comic branding."""
        # Gradient-like top bar (dark background)
        self.set_fill_color(15, 15, 30)
        self.rect(0, 0, 210, 18, style="F")

        # Title
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 215, 0)  # Gold
        self.set_y(4)
        self.cell(0, 10, self.comic_title, align="C")

        # Reset text color
        self.set_text_color(0, 0, 0)
        self.ln(8)

    def footer(self):
        """Custom footer."""
        self.set_y(-15)
        self.set_fill_color(15, 15, 30)
        self.rect(0, 282, 210, 15, style="F")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(255, 215, 0)
        self.cell(0, 10, f"ComicCraft AI  |  Page {self.page_no()} / {{nb}}", align="C")
        self.set_text_color(0, 0, 0)

    def cover_page(self, story_prompt: str, character: str, setting: str, tone: str, art_style: str):
        """Generate a styled cover page."""
        self.add_page()

        # Dark background
        self.set_fill_color(15, 15, 30)
        self.rect(0, 0, 210, 297, style="F")

        # Decorative border
        self.set_draw_color(255, 215, 0)
        self.set_line_width(2)
        self.rect(10, 22, 190, 260)

        # Inner border
        self.set_line_width(0.5)
        self.rect(13, 25, 184, 254)

        # Comic title
        self.set_font("Helvetica", "B", 32)
        self.set_text_color(255, 215, 0)
        self.set_y(50)
        self.cell(0, 20, "COMICCRAFT", align="C")

        self.set_font("Helvetica", "B", 16)
        self.set_text_color(200, 180, 255)
        self.set_y(75)
        self.cell(0, 10, "AI COMIC STORY CREATOR", align="C")

        # Decorative divider
        self.set_draw_color(255, 215, 0)
        self.set_line_width(1)
        self.line(40, 92, 170, 92)

        # Comic info box
        self.set_fill_color(25, 25, 50)
        self.set_draw_color(100, 100, 200)
        self.set_line_width(0.5)
        self.rect(25, 100, 160, 120, style="FD")

        self.set_font("Helvetica", "B", 11)
        self.set_text_color(255, 215, 0)
        self.set_y(108)
        self.cell(0, 8, "YOUR COMIC STORY", align="C")

        self.set_y(120)
        self.set_font("Helvetica", "", 10)

        info_items = [
            ("Story Prompt:", _clean_text(story_prompt[:80] + ("..." if len(story_prompt) > 80 else ""))),
            ("Main Character:", _clean_text(character)),
            ("Setting:", _clean_text(setting.capitalize())),
            ("Story Tone:", _clean_text(tone.capitalize())),
            ("Art Style:", _clean_text(art_style.capitalize())),
        ]

        for label, value in info_items:
            self.set_text_color(180, 180, 255)
            self.set_font("Helvetica", "B", 10)
            self.set_x(35)
            self.cell(55, 9, label)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(255, 255, 255)
            self.multi_cell(100, 9, value)

        # Powered by
        self.set_y(235)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(150, 150, 200)
        self.cell(0, 8, "Powered by Google Gemini AI + Stable Diffusion", align="C")

        self.set_y(248)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 150)
        self.cell(0, 8, "Generated with ComicCraft  -  comiccraft.ai", align="C")


def save_pdf(
    layout: List[Dict[str, Any]],
    story_prompt: str = "",
    character: str = "Hero",
    setting: str = "Unknown",
    tone: str = "Adventure",
    art_style: str = "Comic Book",
) -> str:
    """
    Compile the complete comic into a multi-page PDF.

    Args:
        layout:       List of panel layout dicts from build_comic_layout().
        story_prompt: Original user story prompt.
        character:    Main character name.
        setting:      Story setting.
        tone:         Story tone.
        art_style:    Art style chosen.

    Returns:
        File path to the saved PDF (e.g., 'static/exports/comic_1234567890.pdf').
    """
    timestamp = int(time.time())
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORTS_DIR, filename)

    comic_title = f"{character}'s Adventure"
    pdf = ComicPDF(title=comic_title)
    pdf.alias_nb_pages()

    # Cover page
    pdf.cover_page(story_prompt, character, setting, tone, art_style)

    # One page per panel
    for panel in layout:
        pdf.add_page()
        _render_panel_page(pdf, panel)

    # Final page
    _add_final_page(pdf)

    pdf.output(pdf_path)
    logger.info("PDF saved to: %s", pdf_path)
    return pdf_path


def _render_panel_page(pdf: ComicPDF, panel: Dict[str, Any]):
    """Render a single panel as a PDF page."""
    panel_num = panel.get("panel_number", "?")
    title = _clean_text(str(panel.get("title", f"Panel {panel_num}")))
    scene_desc = _clean_text(str(panel.get("scene_description", "")))
    caption = _clean_text(str(panel.get("caption", "")))
    narration = _clean_text(str(panel.get("narration", "")))
    image_prompt = _clean_text(str(panel.get("image_prompt", "")))
    image_file_path = panel.get("image_file_path", "")

    page_width = 210
    y_cursor = 22

    # Panel header bar
    pdf.set_fill_color(25, 25, 60)
    pdf.set_y(y_cursor)
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 215, 0)
    pdf.cell(190, 10, f"  Panel {panel_num}: {title}", align="L", fill=True)
    y_cursor += 14

    # Comic image
    image_width = 130
    image_height = 90
    image_x = (page_width - image_width) / 2

    if image_file_path and os.path.exists(image_file_path):
        try:
            pdf.image(image_file_path, x=image_x, y=y_cursor, w=image_width, h=image_height)
        except Exception as e:
            logger.warning("Could not embed image %s: %s", image_file_path, e)
            _draw_image_placeholder(pdf, image_x, y_cursor, image_width, image_height, panel_num)
    else:
        _draw_image_placeholder(pdf, image_x, y_cursor, image_width, image_height, panel_num)

    # Image caption box
    img_caption_y = y_cursor + image_height + 2
    pdf.set_fill_color(240, 240, 255)
    pdf.set_draw_color(100, 100, 200)
    pdf.set_line_width(0.3)
    pdf.rect(10, img_caption_y, 190, 8, style="FD")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(80, 80, 120)
    pdf.set_y(img_caption_y + 1)
    pdf.set_x(12)
    short_prompt = (image_prompt[:100] + "...") if len(image_prompt) > 100 else image_prompt
    pdf.cell(186, 6, f"Image Prompt: {short_prompt}", align="L")

    y_cursor = img_caption_y + 12

    # Scene description
    if scene_desc:
        pdf.set_fill_color(245, 245, 255)
        pdf.set_draw_color(180, 180, 220)
        pdf.set_line_width(0.5)
        pdf.set_y(y_cursor)
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(50, 50, 120)
        pdf.cell(190, 7, "Scene Description", fill=True, border=1)
        pdf.set_y(y_cursor + 7)
        pdf.set_x(10)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(60, 60, 80)
        pdf.multi_cell(190, 6, scene_desc, border=1)
        y_cursor = pdf.get_y() + 3

    # Caption
    if caption:
        pdf.set_y(y_cursor)
        pdf.set_x(10)
        pdf.set_fill_color(255, 250, 230)
        pdf.set_draw_color(220, 180, 50)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(120, 80, 0)
        pdf.cell(190, 7, "Caption", fill=True, border=1)
        pdf.set_y(pdf.get_y())
        pdf.set_x(10)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(80, 60, 0)
        pdf.multi_cell(190, 6, caption, border=1)
        y_cursor = pdf.get_y() + 3

    # Narration
    if narration:
        pdf.set_y(y_cursor)
        pdf.set_x(10)
        pdf.set_fill_color(230, 245, 255)
        pdf.set_draw_color(50, 100, 200)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(0, 60, 120)
        pdf.cell(190, 7, "Narration", fill=True, border=1)
        pdf.set_y(pdf.get_y())
        pdf.set_x(10)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 40, 80)
        pdf.multi_cell(190, 6, narration, border=1)


def _draw_image_placeholder(
    pdf: ComicPDF, x: float, y: float, w: float, h: float, panel_num: int
):
    """Draw a styled placeholder rectangle when image is missing."""
    pdf.set_fill_color(30, 30, 60)
    pdf.set_draw_color(255, 215, 0)
    pdf.set_line_width(1)
    pdf.rect(x, y, w, h, style="FD")

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 215, 0)
    pdf.set_y(y + h / 2 - 8)
    pdf.set_x(x)
    pdf.cell(w, 16, f"[ PANEL {panel_num} IMAGE ]", align="C")


def _add_final_page(pdf: ComicPDF):
    """Add a closing / credits page."""
    pdf.add_page()

    pdf.set_fill_color(15, 15, 30)
    pdf.rect(0, 0, 210, 297, style="F")

    pdf.set_draw_color(255, 215, 0)
    pdf.set_line_width(2)
    pdf.rect(10, 22, 190, 260)

    pdf.set_y(80)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 20, "THE END", align="C")

    pdf.set_y(110)
    pdf.set_font("Helvetica", "I", 14)
    pdf.set_text_color(200, 180, 255)
    pdf.cell(0, 10, "Thank you for creating with ComicCraft!", align="C")

    pdf.set_y(135)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(150, 150, 200)
    pdf.cell(0, 8, "Your story. Your imagination. AI-powered.", align="C")

    pdf.set_y(200)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 150)
    pdf.cell(0, 8, "Powered by Google Gemini AI + Stable Diffusion", align="C")

    pdf.set_y(215)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 120)
    pdf.cell(0, 8, "ComicCraft - AI Comic Story Creator", align="C")
