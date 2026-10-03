"""
image_generator.py
Generates comic-style illustrations using either:
  - Hugging Face Inference API (default, cloud-based, no GPU required)
  - Local Stable Diffusion via diffusers (optional, requires GPU)

The generated image is saved to static/panels/ and the file path is returned.
"""

import io
import os
import re
import logging
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import requests

from app.config import (
    HF_API_KEY,
    HF_IMAGE_MODEL,
    PANELS_DIR,
    USE_HF_INFERENCE_API,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
)

logger = logging.getLogger(__name__)

# Ensure panels directory exists
Path(PANELS_DIR).mkdir(parents=True, exist_ok=True)


def _sanitize_filename(text: str) -> str:
    """Convert a prompt to a safe filename."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s]+", "_", text.strip())
    return text[:60]


def generate_image(image_prompt: str, panel_number: int = 1) -> str:
    """
    Generate a comic-style illustration from the given prompt.

    Args:
        image_prompt: Detailed artistic prompt for image generation.
        panel_number: Panel number (used in filename).

    Returns:
        Relative file path to the saved image (e.g., 'static/panels/panel_1_xyz.png').
        Falls back to a placeholder image if generation fails.
    """
    timestamp = int(time.time())
    safe_name = _sanitize_filename(image_prompt)
    filename = f"panel_{panel_number}_{safe_name}_{timestamp}.jpg"
    filepath = os.path.join(PANELS_DIR, filename)

    is_valid_token = HF_API_KEY and HF_API_KEY != "your_huggingface_api_token_here"
    if USE_HF_INFERENCE_API and is_valid_token:
        success = _generate_via_hf_api(image_prompt, filepath)
    else:
        if not is_valid_token:
            logger.info("HF_API_KEY is not configured or is a placeholder. Using fallback.")
        success = _generate_locally(image_prompt, filepath)

    if not success:
        logger.warning("Image generation failed for panel %d. Using placeholder.", panel_number)
        filepath = _create_placeholder(panel_number, image_prompt)

    return filepath


# ---------------------------------------------------------------------------
# Hugging Face Inference API (recommended — no GPU required)
# ---------------------------------------------------------------------------

def _generate_via_hf_api(prompt: str, output_path: str) -> bool:
    """Call HF Inference API using InferenceClient to generate an image."""
    enhanced_prompt = (
        f"{prompt}, comic book art style, vibrant colors, bold lines, "
        "high quality, detailed illustration, professional artwork"
    )

    models_to_try = [
        "black-forest-labs/FLUX.1-schnell",
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
    ]

    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=HF_API_KEY)
        for model_id in models_to_try:
            for attempt in range(3):
                try:
                    logger.info("Generating image with HF model %s (attempt %d/3)...", model_id, attempt + 1)
                    image = client.text_to_image(enhanced_prompt, model=model_id)
                    # Optimize size for comic panels and lightning-fast PDF compilation
                    if image.width > 768 or image.height > 768:
                        image.thumbnail((768, 768), Image.Resampling.LANCZOS)
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    image.save(output_path, "JPEG", quality=85, optimize=True)
                    logger.info("Image saved successfully to %s", output_path)
                    return True
                except Exception as e:
                    logger.warning("InferenceClient error with %s (attempt %d/3): %s", model_id, attempt + 1, e)
                    if "429" in str(e) or "503" in str(e) or "rate" in str(e).lower() or "loading" in str(e).lower():
                        time.sleep(2 * (attempt + 1))
                        continue
                    break
    except Exception as e:
        logger.error("HF InferenceClient error: %s", e)

    return False


# ---------------------------------------------------------------------------
# Local Stable Diffusion (requires GPU / significant RAM)
# ---------------------------------------------------------------------------

def _generate_locally(prompt: str, output_path: str) -> bool:
    """Generate image using local Stable Diffusion via diffusers."""
    try:
        import torch
        from diffusers import StableDiffusionPipeline

        enhanced_prompt = (
            f"{prompt}, comic book art, vibrant, bold lines, detailed, "
            "high quality illustration"
        )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        logger.info("Loading Stable Diffusion pipeline on %s...", device)
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=dtype,
            safety_checker=None,
        ).to(device)

        result = pipe(
            prompt=enhanced_prompt,
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
            num_inference_steps=30,
            guidance_scale=7.5,
        )
        image = result.images[0]
        image.save(output_path)
        logger.info("Local SD image saved to %s", output_path)
        return True

    except ImportError:
        logger.warning("diffusers/torch not installed. Cannot use local SD.")
        return False
    except Exception as e:
        logger.error("Local SD error: %s", e)
        return False


# ---------------------------------------------------------------------------
# Placeholder image generator (always works as fallback)
# ---------------------------------------------------------------------------

def _create_placeholder(panel_number: int, prompt: str) -> str:
    """Create a styled placeholder image when AI generation is unavailable."""
    colors = [
        "#1a1a2e", "#16213e", "#0f3460", "#533483", "#e94560"
    ]
    bg_color = colors[(panel_number - 1) % len(colors)]

    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw comic-style border
    border_color = "#FFD700"
    for i in range(3):
        draw.rectangle(
            [i * 4, i * 4, IMAGE_WIDTH - i * 4 - 1, IMAGE_HEIGHT - i * 4 - 1],
            outline=border_color,
            width=2,
        )

    # Comic dots pattern
    dot_color = "#ffffff22"
    for x in range(20, IMAGE_WIDTH, 30):
        for y in range(20, IMAGE_HEIGHT, 30):
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=dot_color)

    # Panel label
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    panel_text = f"PANEL {panel_number}"
    draw.text((IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2 - 40), panel_text,
              fill="#FFD700", font=font_large, anchor="mm")

    # Truncate prompt display
    short_prompt = (prompt[:80] + "...") if len(prompt) > 80 else prompt
    words = short_prompt.split()
    lines, current = [], []
    for word in words:
        current.append(word)
        if len(" ".join(current)) > 35:
            lines.append(" ".join(current[:-1]))
            current = [word]
    if current:
        lines.append(" ".join(current))

    y_start = IMAGE_HEIGHT // 2 + 20
    for line in lines[:4]:
        draw.text((IMAGE_WIDTH // 2, y_start), line, fill="#ffffff",
                  font=font_small, anchor="mm")
        y_start += 22

    # Comic label at bottom
    draw.text((IMAGE_WIDTH // 2, IMAGE_HEIGHT - 30), "⚡ ComicCraft AI ⚡",
              fill="#FFD700", font=font_small, anchor="mm")

    timestamp = int(time.time())
    filename = f"placeholder_{panel_number}_{timestamp}.png"
    filepath = os.path.join(PANELS_DIR, filename)
    img.save(filepath)
    logger.info("Placeholder image created: %s", filepath)
    return filepath
