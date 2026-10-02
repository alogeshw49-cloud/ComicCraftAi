"""
routes.py
Main FastAPI router containing all application routes:
  GET  /                  → Homepage (index.html)
  POST /generate          → Form-based comic generation (comic_preview.html)
  POST /generate-comic/json → JSON API comic generation
  GET  /export-success    → Export success confirmation page
  GET  /test-image        → Developer image generation test
  GET  /download-pdf      → Serve the PDF file for download
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from concurrent.futures import ThreadPoolExecutor

from app.schemas import PromptRequest
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _generate_images_in_parallel(panels):
    """Generate all comic panel illustrations simultaneously in parallel for maximum speed."""
    logger.info("Starting concurrent generation for %d panel images...", len(panels))
    with ThreadPoolExecutor(max_workers=min(len(panels), 5)) as executor:
        future_to_idx = {
            executor.submit(
                generate_image,
                panel["image_prompt"],
                panel["panel_number"],
            ): idx
            for idx, panel in enumerate(panels)
        }
        image_paths = [None] * len(panels)
        for future, idx in future_to_idx.items():
            image_paths[idx] = future.result()
        return image_paths

# ---------------------------------------------------------------------------
# GET / — Homepage
# ---------------------------------------------------------------------------

@router.get("/", tags=["Frontend"])
async def homepage(request: Request):
    """Render the homepage with the comic creation form."""
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# POST /generate — Form-based Comic Generation
# ---------------------------------------------------------------------------

@router.post("/generate", tags=["Comic Generation"])
async def generate_comic_form(
    request: Request,
    prompt: str = Form(..., description="Story prompt"),
    character: str = Form(default="Hero", description="Main character name"),
    setting: str = Form(default="forest", description="Story setting"),
    tone: str = Form(default="dramatic", description="Story tone"),
    art_style: str = Form(default="comic book", description="Art style"),
):
    """
    Handle form submission from index.html.
    Generates the complete comic and renders comic_preview.html.
    """
    try:
        logger.info(
            "Starting comic generation | prompt=%r | character=%r | setting=%r | tone=%r | art=%r",
            prompt, character, setting, tone, art_style,
        )

        # Step 1: Generate structured panel outline (Gemini Flash)
        outline = generate_outline(prompt, character, setting, tone, art_style)
        logger.info("Outline generated: %d panels", len(outline))

        # Step 2: Enrich with narration & dialogue (Gemini Pro)
        enriched_panels = generate_story(outline, character, tone)
        logger.info("Story narration generated")

        # Step 3: Generate panel images concurrently in parallel (blazing fast)
        image_paths = _generate_images_in_parallel(enriched_panels)
        logger.info("All %d panel images generated concurrently.", len(image_paths))

        # Step 4: Build structured layout
        layout = build_comic_layout(enriched_panels, image_paths)

        # Step 5: Export to PDF
        pdf_path = save_pdf(layout, prompt, character, setting, tone, art_style)
        logger.info("PDF exported: %s", pdf_path)

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "layout": layout,
                "pdf_path": pdf_path,
                "character": character,
                "setting": setting,
                "tone": tone,
                "art_style": art_style,
                "prompt": prompt,
            },
        )

    except Exception as e:
        logger.error("Error generating comic: %s", e, exc_info=True)
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500,
        )


# ---------------------------------------------------------------------------
# POST /generate-comic/json — JSON API Comic Generation
# ---------------------------------------------------------------------------

@router.post("/generate-comic/json", tags=["API"])
async def generate_comic_json(body: PromptRequest):
    """
    JSON API endpoint. Accepts a PromptRequest body and returns
    the comic layout and PDF path as JSON.
    """
    try:
        logger.info("JSON API comic generation: %s", body.prompt)

        outline = generate_outline(
            body.prompt, body.character, body.setting, body.tone, body.art_style
        )
        enriched_panels = generate_story(outline, body.character, body.tone)

        image_paths = _generate_images_in_parallel(enriched_panels)

        layout = build_comic_layout(enriched_panels, image_paths)
        pdf_path = save_pdf(layout, body.prompt, body.character, body.setting, body.tone, body.art_style)

        return JSONResponse(
            content={
                "success": True,
                "layout": layout,
                "pdf_path": pdf_path,
                "message": "Comic generated successfully",
            }
        )

    except Exception as e:
        logger.error("JSON API error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# GET /export-success — Export Success Page
# ---------------------------------------------------------------------------

@router.get("/export-success", tags=["Frontend"])
async def export_success(request: Request, pdf_path: Optional[str] = None):
    """Render the export success confirmation page."""
    return templates.TemplateResponse(
        "export_success.html",
        {"request": request, "pdf_path": pdf_path},
    )


# ---------------------------------------------------------------------------
# GET /download-pdf — PDF Download
# ---------------------------------------------------------------------------

@router.get("/download-pdf", tags=["Export"])
async def download_pdf(pdf_path: str):
    """
    Serve the generated PDF file as a downloadable attachment.
    The pdf_path query param is the filesystem path to the PDF.
    """
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    # Basic path traversal protection
    abs_path = os.path.abspath(pdf_path)
    exports_abs = os.path.abspath("static/exports")
    if not abs_path.startswith(exports_abs):
        raise HTTPException(status_code=403, detail="Access denied")

    filename = os.path.basename(pdf_path)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# GET /test-image — Developer Image Test Route
# ---------------------------------------------------------------------------

@router.get("/test-image", tags=["Developer"])
async def test_image(request: Request, img_prompt: Optional[str] = None):
    """
    Developer utility: test image generation with a custom prompt.
    Returns a rendered page showing the generated image.
    """
    test_prompt = img_prompt or "A brave fox in an enchanted forest, anime style, vibrant colors"

    try:
        image_path = generate_image(test_prompt, panel_number=0)
        # Normalize to web URL
        web_path = image_path.replace("\\", "/")
        if not web_path.startswith("/"):
            web_path = "/" + web_path

        return templates.TemplateResponse(
            "test_image.html",
            {
                "request": request,
                "image_path": web_path,
                "prompt": test_prompt,
            },
        )
    except Exception as e:
        logger.error("Test image error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
