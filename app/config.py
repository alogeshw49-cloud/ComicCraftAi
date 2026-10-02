"""
ComicCraft Configuration
Loads environment variables and provides app-wide settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
HF_API_KEY: str = os.getenv("HF_API_KEY", "")

# Model names
GEMINI_FLASH_MODEL: str = os.getenv("GEMINI_FLASH_MODEL", "gemini-flash-lite-latest")
GEMINI_PRO_MODEL: str = os.getenv("GEMINI_PRO_MODEL", "gemini-flash-lite-latest")
STABLE_DIFFUSION_MODEL: str = "runwayml/stable-diffusion-v1-5"

# Paths
STATIC_DIR: str = "static"
PANELS_DIR: str = "static/panels"
EXPORTS_DIR: str = "static/exports"
TEMPLATES_DIR: str = "templates"

# Comic settings
NUM_PANELS: int = 5

# Image generation settings
IMAGE_WIDTH: int = 512
IMAGE_HEIGHT: int = 512
NUM_INFERENCE_STEPS: int = 30
GUIDANCE_SCALE: float = 7.5

# Use HF Inference API instead of local Stable Diffusion (lighter weight)
USE_HF_INFERENCE_API: bool = True
HF_IMAGE_MODEL: str = "stabilityai/stable-diffusion-xl-base-1.0"
