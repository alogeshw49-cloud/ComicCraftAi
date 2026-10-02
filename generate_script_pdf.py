"""
generate_script_pdf.py
Compiles the 5-Minute Demo Video Script into a clean, professional PDF.
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def clean(txt: str) -> str:
    """Sanitize strings for core FPDF font encoding (latin-1)."""
    if not txt:
        return ""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2014": "--", "\u2013": "-",
        "\u2026": "...", "\u2022": "*",
        "⚡": "", "🎉": "", "🚀": "", "📄": "",
        "👁️": "", "⬇️": "", "✅": "", "✓": "*",
        "🥷": "", "⚔️": "", "⏳": "", "•": "-",
        "—": "--", "–": "-", "“": '"', "”": '"',
        "‘": "'", "’": "'"
    }
    for old, new in replacements.items():
        txt = txt.replace(old, new)
    return txt.encode("latin-1", "replace").decode("latin-1")


class ScriptPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 6, clean("ComicCraft AI -- 5-Minute Technical Demo Video Script"), align="L",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(226, 232, 240)
            self.set_line_width(0.3)
            self.line(15, 14, 195, 14)
            self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, f"Page {self.page_no()} of {{nb}}", align="C")


def build_pdf():
    pdf = ScriptPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(15, 12, 15)

    # ═══════════════════════════════════════════════════════════
    # PAGE 1: TITLE & OVERVIEW TABLE
    # ═══════════════════════════════════════════════════════════
    pdf.add_page()

    # Dark Header Banner
    pdf.set_fill_color(15, 23, 42)  # Slate 900
    pdf.rect(15, 12, 180, 36, style="F")

    pdf.set_xy(20, 16)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(170, 8, clean("COMICCRAFT AI -- 5-MINUTE TECHNICAL DEMO SCRIPT"), align="L")

    pdf.set_xy(20, 25)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(52, 211, 153)  # Mint Green
    pdf.cell(170, 6, clean("Target Duration: Exactly 5:00 Minutes | Natural Speaking Pace (135-140 WPM)"), align="L")

    pdf.set_xy(20, 32)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(170, 6, clean("Source of Truth: ComicCraft AI Codebase (FastAPI, Google Gemini, FLUX.1-schnell, FPDF2)"), align="L")

    pdf.set_y(52)

    # Overview Table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, clean("Demo Timeline & Flowchart"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    timeline_data = [
        ("Section 1: Introduction & Project Purpose", "0:00 - 0:35", "35 sec"),
        ("Section 2: Codebase Architecture in VS Code", "0:35 - 1:30", "55 sec"),
        ("Section 3: Core Technical Pipeline & Model Config", "1:30 - 2:20", "50 sec"),
        ("Section 4: Starting the Backend Server & Logs", "2:20 - 2:50", "30 sec"),
        ("Section 5: Live Generation Workflow (Prompt to Comic)", "2:50 - 3:55", "65 sec"),
        ("Section 6: Model Selection & Fallback Resilience", "3:55 - 4:30", "35 sec"),
        ("Section 7: Final PDF Export & Project Summary", "4:30 - 5:00", "30 sec"),
    ]

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(110, 6.5, clean("  Section Title"), border=1, fill=True)
    pdf.cell(40, 6.5, clean("Timestamp"), border=1, fill=True, align="C")
    pdf.cell(30, 6.5, clean("Duration"), border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 8.5)
    for title, ts, dur in timeline_data:
        pdf.set_text_color(15, 23, 42)
        pdf.cell(110, 6, clean(f"  {title}"), border=1)
        pdf.cell(40, 6, clean(ts), border=1, align="C")
        pdf.cell(30, 6, clean(dur), border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    # ═══════════════════════════════════════════════════════════
    # SECTION CONTENT
    # ═══════════════════════════════════════════════════════════
    sections = [
        (
            "Section 1: Introduction & Project Purpose",
            "0:00 - 0:35",
            "35 sec",
            "Open browser to ComicCraft AI homepage (http://localhost:8000). Slowly scroll past hero headline, art style selector cards, and story prompt form.",
            "\"Hello everyone! Welcome to the technical demonstration of ComicCraft AI -- an end-to-end Generative AI platform that turns simple story prompts into complete, multi-panel comic books with original artwork, character dialogue, and print-ready PDFs.\n\nCreating a comic traditionally requires writers, storyboard artists, illustrators, and layout designers. ComicCraft AI orchestrates state-of-the-art Large Language Models and diffusion models into an automated storytelling pipeline.\n\nToday, I will walk you through our codebase architecture, our AI integrations, and run a complete live generation from prompt to multi-page comic.\""
        ),
        (
            "Section 2: Codebase Structure & Key Files in VS Code",
            "0:35 - 1:30",
            "55 sec",
            "Switch to VS Code. Expand explorer: highlight app/ folder, app/main.py, app/config.py (lines 12-18), templates/, and static/.",
            "\"Let us look under the hood inside VS Code. The project follows a clean, modular Python and FastAPI architecture:\n* Our entry point is app/main.py. It initializes FastAPI, mounts our static directory, and configures CORS and GZip middleware for optimal performance.\n* Application settings live in app/config.py, where environment variables are loaded securely at runtime via python-dotenv.\n* The app/ package handles backend logic: gemini_flash.py builds the outline, gemini_pro.py expands the narrative, image_generator.py handles image synthesis, layout_builder.py structures the panels, and exporters.py compiles the PDF.\n* On the frontend, we use semantic HTML5 Jinja2 templates in templates/ paired with custom vanilla CSS and JavaScript in static/ for a responsive, modern dark-mode experience.\""
        ),
        (
            "Section 3: Core Technical Pipeline & Model Configuration",
            "1:30 - 2:20",
            "50 sec",
            "Open app/gemini_flash.py (show JSON prompt), app/image_generator.py (show InferenceClient + FLUX.1-schnell), and app/exporters.py (ComicPDF class).",
            "\"Here are the three critical technical components powering our system:\n\n1. Structured Storyboarding: In gemini_flash.py, we prompt Google Gemini model with a strict JSON schema. It returns an exact 5-panel sequence, with scene descriptions and tailored visual prompts for every panel.\n\n2. AI Image Generation: In image_generator.py, we integrate the Hugging Face InferenceClient connected to FLUX.1-schnell. This produces 1024-by-1024 high-resolution comic illustrations in seconds. If unauthenticated, it gracefully falls back to dynamic styled vector placeholders without crashing.\n\n3. Document Compilation: In exporters.py, our custom ComicPDF engine built on FPDF2 sanitizes all unicode strings and formats panel images, speech bubbles, and captions into an A4 multi-page document.\""
        ),
        (
            "Section 4: Starting the Backend Server & Logs",
            "2:20 - 2:50",
            "30 sec",
            "Open VS Code terminal. Run: uvicorn app.main:app --reload. Point out startup logs: ComicCraft AI -- Starting up, Homepage: http://127.0.0.1:8000.",
            "\"Now let us launch the backend.\n\nIn the terminal, we start our development server using uvicorn app.main:app --reload.\n\nAs you can see from the logs, Uvicorn initializes the application on port 8000, mounts our static panel and export directories, and registers our route handlers.\n\nLet us switch over to the browser.\""
        ),
        (
            "Section 5: Live Generation Workflow (Prompt to Comic)",
            "2:50 - 3:55",
            "65 sec",
            "Fill form on http://localhost:8000 (Prompt: lone wandering knight with glowing blade ascends mountain to confront shadow titan; Character: Loki; Setting: Deep Space; Tone: Adventurous; Art Style: Comic Book). Click Generate. Show step progress overlay, then scroll generated preview panels.",
            "\"Here on the homepage, we enter our story prompt: a wandering knight carrying an enchanted blade confronting a shadow titan. We specify the character name, setting, adventurous tone, and choose the Comic Book art style.\n\nWhen I click Generate Comic Story, our frontend displays a step-by-step progress overlay while the backend executes the pipeline asynchronously.\n\nAnd here is the result! In under a minute, we have 5 panels. Notice how Gemini crafted cohesive titles, ambient captions, and character dialogue across each panel, while FLUX.1 rendered matching illustrations featuring our knight and the glowing blade.\""
        ),
        (
            "Section 6: Model Selection & Fallback Architecture",
            "3:55 - 4:30",
            "35 sec",
            "Briefly show app/config.py (lines 14-17 showing gemini-flash-lite-latest) and _fallback_outline() in app/gemini_flash.py.",
            "\"A key architectural feature of ComicCraft AI is model resilience.\n\nDuring startup, we evaluate Gemini models in ascending order -- starting from the lowest-cost tier upward -- to automatically select the most efficient active model. In our environment, gemini-flash-lite-latest is dynamically selected, ensuring low latency and high quality.\n\nFurthermore, in gemini_flash.py, we implement a robust fallback handler. If an API rate limit or network timeout ever occurs, the system automatically catches the exception and generates a structured fallback narrative, guaranteeing that the end user never encounters a blank screen or a broken application.\""
        ),
        (
            "Section 7: Final Output, PDF Export & Project Summary",
            "4:30 - 5:00",
            "30 sec",
            "Click Download Comic PDF button. Point directly to Green Panel Download Success Modal with animated checkmark and confetti. Click Open/View PDF to view the compiled PDF in a new tab.",
            "\"Finally, let us export our comic.\n\nWhen I click Download Comic PDF, the file download begins, and our custom Green Success Panel immediately pops up with celebratory confetti. It confirms the download, displays file metadata, and lets us open the PDF directly in a new tab.\n\nLooking at the generated PDF, we have a custom cover page, styled borders, embedded illustrations, and formatted speech bubbles.\n\nIn summary, ComicCraft AI delivers a full-stack, modular, and resilient Generative AI application combining Gemini and FLUX.1. Thank you for watching!\""
        ),
    ]

    for title, ts, dur, action, speech in sections:
        # Check space needed for header + action + speech (~75mm)
        if pdf.get_y() > 215:
            pdf.add_page()

        # Section Header Pill
        pdf.set_fill_color(241, 245, 249)
        pdf.set_draw_color(16, 185, 129)
        pdf.set_line_width(0.8)
        pdf.rect(15, pdf.get_y(), 180, 7.5, style="FD")

        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(130, 7.5, clean(f"  {title}"), align="L")
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(5, 150, 105)
        pdf.cell(50, 7.5, clean(f"[{ts} | {dur}]  "), align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1.5)

        # Action block
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 4.5, clean("  WHAT TO DO ON SCREEN (VISUAL CUE):"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.set_line_width(0.2)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(180, 4.5, clean(f"  {action}"), border=1, fill=True)
        pdf.ln(2)

        # Speech block
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(16, 185, 129)
        pdf.cell(0, 4.5, clean("  WHAT TO SAY (SPOKEN SCRIPT):"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(16, 185, 129)
        pdf.set_line_width(0.3)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(180, 4.8, clean(speech), border=1, fill=True)
        pdf.ln(4)

    # ═══════════════════════════════════════════════════════════
    # PRESENTATION TIPS BOX (PAGE 4 / END)
    # ═══════════════════════════════════════════════════════════
    if pdf.get_y() > 230:
        pdf.add_page()

    pdf.set_fill_color(240, 253, 244)  # Light mint
    pdf.set_draw_color(34, 197, 94)
    pdf.set_line_width(0.6)
    box_y = pdf.get_y()
    pdf.rect(15, box_y, 180, 32, style="FD")

    pdf.set_xy(18, box_y + 2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(22, 101, 52)
    pdf.cell(174, 5, clean("KEY RECORDING & PRESENTATION TIPS:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(21, 128, 61)
    tips = [
        "* Terminal Setup: Run 'source env/bin/activate' beforehand and clear terminal before recording.",
        "* Browser Zoom: Set browser zoom to 105% or 110% for crisp text and image visibility on 1080p/4K displays.",
        "* Green Popup Pause: Let the green success modal and confetti stay on screen for 3 seconds before opening the PDF.",
        "* Natural Pacing: Speak with steady rhythm (~135 WPM). The timings allow natural pauses between sections."
    ]
    for tip in tips:
        pdf.set_x(18)
        pdf.cell(174, 4.5, clean(tip), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Save to disk
    out_1 = "/home/logeswaran-a/Desktop/ComicCraftAi/ComicCraft_Demo_Video_Script.pdf"
    out_2 = "/home/logeswaran-a/Desktop/ComicCraftAi/static/exports/ComicCraft_Demo_Video_Script.pdf"

    pdf.output(out_1)
    pdf.output(out_2)
    print(f"Successfully generated {out_1}")
    print(f"Successfully generated {out_2}")
    print(f"Total Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
