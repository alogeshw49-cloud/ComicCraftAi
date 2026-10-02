"""
layout_builder.py
Organizes generated images and full comic story into a structured
panel layout for use in templates and PDF export.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def build_comic_layout(
    enriched_panels: List[Dict[str, Any]],
    image_paths: List[str],
) -> List[Dict[str, Any]]:
    """
    Combine enriched panel data with generated image paths into a
    structured layout ready for template rendering and PDF export.

    Args:
        enriched_panels: Panel dicts (from gemini_pro.generate_story) containing
                         panel_number, title, scene_description, image_prompt,
                         caption, narration.
        image_paths:     List of image file paths, one per panel.

    Returns:
        A list of layout dicts with all panel data plus image_path.
    """
    layout: List[Dict[str, Any]] = []

    for i, panel in enumerate(enriched_panels):
        image_path = image_paths[i] if i < len(image_paths) else ""

        # Normalize the image path for web serving (remove leading 'static/')
        web_image_path = image_path.replace("\\", "/")
        if web_image_path.startswith("static/"):
            web_image_path = "/" + web_image_path

        layout_panel = {
            "panel_number": panel.get("panel_number", i + 1),
            "title": panel.get("title", f"Panel {i + 1}"),
            "scene_description": panel.get("scene_description", ""),
            "image_prompt": panel.get("image_prompt", ""),
            "caption": panel.get("caption", ""),
            "narration": panel.get("narration", ""),
            "image_path": web_image_path,           # Web URL path (for templates)
            "image_file_path": image_path,          # Filesystem path (for PDF export)
        }
        layout.append(layout_panel)
        logger.debug("Layout built for panel %d", layout_panel["panel_number"])

    logger.info("Comic layout built with %d panels.", len(layout))
    return layout
