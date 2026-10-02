"""
gemini_flash.py
Uses Gemini 1.5 Flash to generate a structured 5-panel comic outline
based on the user's story prompt, character, setting, tone, and art style.
"""

import json
import re
import logging
from typing import List, Dict, Any

import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_FLASH_MODEL, NUM_PANELS

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


def generate_outline(
    prompt: str,
    character: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[Dict[str, Any]]:
    """
    Generate a structured 5-panel comic outline using Gemini Flash.

    Args:
        prompt:    The user's story idea.
        character: Main character name.
        setting:   Story location (e.g., forest, space, city).
        tone:      Story mood (e.g., dramatic, funny, poetic).
        art_style: Visual style (e.g., anime, comic book, pixel art, realistic).

    Returns:
        A list of panel dicts with keys:
            - panel_number (int)
            - title (str)
            - scene_description (str)
            - image_prompt (str)
    """
    system_prompt = f"""You are a professional comic book writer and storyboard artist.
Generate a structured {NUM_PANELS}-panel comic outline for the following story.

Story Prompt: {prompt}
Main Character: {character}
Setting: {setting}
Tone: {tone}
Art Style: {art_style}

Respond ONLY with valid JSON (no markdown fences, no explanation).
Return a JSON array with exactly {NUM_PANELS} panel objects.
Each panel object must have these exact keys:
  - "panel_number": integer (1 to {NUM_PANELS})
  - "title": short panel title (string)
  - "scene_description": 2-3 sentences describing the scene (string)
  - "image_prompt": a vivid, detailed prompt for image generation in {art_style} style (string)

Example format:
[
  {{
    "panel_number": 1,
    "title": "The Beginning",
    "scene_description": "Description here.",
    "image_prompt": "Detailed image generation prompt here."
  }}
]
"""

    try:
        model = genai.GenerativeModel(GEMINI_FLASH_MODEL)
        response = model.generate_content(system_prompt)
        raw_text = response.text.strip()

        # Strip markdown code fences if present
        raw_text = re.sub(r"^```[a-z]*\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text)
        raw_text = raw_text.strip()

        panels: List[Dict[str, Any]] = json.loads(raw_text)

        # Validate structure
        validated: List[Dict[str, Any]] = []
        for i, panel in enumerate(panels[:NUM_PANELS], start=1):
            validated.append(
                {
                    "panel_number": panel.get("panel_number", i),
                    "title": panel.get("title", f"Panel {i}"),
                    "scene_description": panel.get("scene_description", ""),
                    "image_prompt": panel.get("image_prompt", f"{art_style} style comic panel"),
                }
            )

        logger.info("Generated %d panel outlines successfully.", len(validated))
        return validated

    except json.JSONDecodeError as e:
        logger.error("JSON decode error in generate_outline: %s\nRaw: %s", e, raw_text)
        # Fallback: return a generic outline
        return _fallback_outline(prompt, character, setting, tone, art_style)
    except Exception as e:
        logger.error("Error in generate_outline: %s", e)
        return _fallback_outline(prompt, character, setting, tone, art_style)


def _fallback_outline(
    prompt: str,
    character: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[Dict[str, Any]]:
    """Return a fallback outline if Gemini Flash fails."""
    titles = [
        "The Beginning",
        "The Challenge",
        "The Turning Point",
        "The Climax",
        "The Resolution",
    ]
    descriptions = [
        f"{character} starts their journey in {setting}.",
        f"A challenge arises for {character}.",
        f"The story takes a dramatic turn.",
        f"The climax of {character}'s adventure unfolds.",
        f"{character} finds resolution and peace.",
    ]
    return [
        {
            "panel_number": i + 1,
            "title": titles[i],
            "scene_description": descriptions[i],
            "image_prompt": f"{art_style} style: {descriptions[i]} {prompt}",
        }
        for i in range(NUM_PANELS)
    ]
