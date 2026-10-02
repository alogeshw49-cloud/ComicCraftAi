"""
ComicCraft AI — Higgsfield Seedance 2.5 Video Generation Example
================================================================
Uses the official higgsfield-client Python SDK (synchronous subscribe).
Credentials are loaded at runtime from HF_KEY in .env — never logged or printed.

Usage:
    source env/bin/activate
    python higgsfield_seedance.py
"""

import os
import sys
from dotenv import load_dotenv

# ── Load credentials from .env at runtime (server-side only) ──────────────────
load_dotenv()

_hf_key = os.environ.get("HF_KEY", "")
if not _hf_key or ":" not in _hf_key:
    print(
        "ERROR: HF_KEY is missing or malformed in .env\n"
        "Expected format: HF_KEY=key-id:key-secret\n"
        "Set it at: https://open.higgsfield.ai/api-keys",
        file=sys.stderr,
    )
    sys.exit(1)

# Inject into environment so the SDK picks it up automatically
os.environ["HF_KEY"] = _hf_key

# ── Import SDK after setting credential env var ───────────────────────────────
import higgsfield_client  # noqa: E402


def generate_video() -> None:
    """
    Submit a Seedance 2.5 text-to-video request and print the result URL.
    Blocks until the request reaches a terminal state (completed / failed /
    canceled / moderated).
    """
    model = "bytedance/seedance-2.5/text-to-video"

    arguments = {
        "prompt": "A cinematic scene at sunset",
        "duration": 5,
        "resolution": "720p",
        "aspect_ratio": "16:9",
    }

    print(f"Submitting to model: {model}")
    print(f"Prompt: {arguments['prompt']}")
    print(f"Duration: {arguments['duration']}s  |  Resolution: {arguments['resolution']}  |  Aspect: {arguments['aspect_ratio']}")
    print("Waiting for generation (this may take 1–3 minutes)…\n")

    # subscribe() blocks and polls until a terminal state is reached
    result = higgsfield_client.subscribe(model, arguments=arguments)

    status = result.get("status", "unknown")

    if status == "completed":
        videos = result.get("videos") or []
        if videos:
            video_url = videos[0].get("url", "")
            print("✅ Generation completed!")
            print(f"🎬 Video URL: {video_url}")
        else:
            print("✅ Status: completed, but no video URL was returned in the response.")
            print(f"Full result: {result}")

    elif status == "failed":
        error = result.get("error") or result.get("message") or "Unknown error"
        print(f"❌ Generation FAILED: {error}", file=sys.stderr)
        sys.exit(2)

    elif status in ("canceled", "cancelled"):
        print("⚠️  Generation was CANCELED before completion.", file=sys.stderr)
        sys.exit(3)

    elif status in ("nsfw", "moderated"):
        print(
            "⚠️  Generation was MODERATED (content policy). "
            "Try a different prompt.",
            file=sys.stderr,
        )
        sys.exit(4)

    else:
        print(f"⚠️  Unexpected terminal status: '{status}'", file=sys.stderr)
        print(f"Full result: {result}", file=sys.stderr)
        sys.exit(5)


if __name__ == "__main__":
    generate_video()
