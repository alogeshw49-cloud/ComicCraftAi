"""
gemini_pro.py
Uses Gemini 1.5 Pro to expand comic panel outlines into rich,
full-story narration with character dialogues and captions.
"""

import logging
import re
from typing import List, Dict, Any

import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_PRO_MODEL

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)


from concurrent.futures import ThreadPoolExecutor


def _enrich_single_panel(model, panel: Dict[str, Any], character: str, tone: str) -> Dict[str, Any]:
    panel_num = panel.get("panel_number", "?")
    title = panel.get("title", "")
    scene = panel.get("scene_description", "")

    prompt = f"""You are a master comic book storyteller.
Write engaging comic narration for the following panel.

Panel Number: {panel_num}
Panel Title: {title}
Scene Description: {scene}
Main Character: {character}
Story Tone: {tone}

Provide your response in this EXACT format (no extra text):
CAPTION: <A short 1-sentence ambient caption describing the environment or background sounds>
NARRATION: <2-4 sentences of vivid narration including {character}'s actions, emotions, or dialogue>
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        caption = _extract_section(raw, "CAPTION")
        narration = _extract_section(raw, "NARRATION")

        if not caption:
            caption = f"Panel {panel_num}: {title}"
        if not narration:
            narration = scene

    except Exception as e:
        logger.error("Error generating story for panel %s: %s", panel_num, e)
        caption = f"Panel {panel_num}: {title}"
        narration = scene

    enriched = dict(panel)
    enriched["caption"] = caption
    enriched["narration"] = narration
    logger.info("Story generated for panel %s.", panel_num)
    return enriched


def generate_story(
    outline: List[Dict[str, Any]],
    character: str,
    tone: str,
) -> List[Dict[str, Any]]:
    """
    Expand comic panel outlines into detailed narration and dialogue in parallel.
    """
    model = genai.GenerativeModel(GEMINI_PRO_MODEL)

    with ThreadPoolExecutor(max_workers=min(len(outline), 5)) as executor:
        futures = [
            executor.submit(_enrich_single_panel, model, panel, character, tone)
            for panel in outline
        ]
        return [f.result() for f in futures]


def _extract_section(text: str, label: str) -> str:
    """Extract content after a labeled section in the response."""
    pattern = rf"{label}:\s*(.*?)(?=\n[A-Z]+:|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: find line starting with label
    for line in text.splitlines():
        if line.upper().startswith(f"{label}:"):
            return line[len(label) + 1:].strip()
    return ""
