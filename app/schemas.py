"""
schemas.py
Pydantic schemas for request/response validation in FastAPI endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class PromptRequest(BaseModel):
    """JSON body schema for the /generate-comic/json endpoint."""

    prompt: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Main story idea for the comic",
        example="A brave fox exploring an enchanted forest",
    )
    character: str = Field(
        default="Hero",
        min_length=1,
        max_length=100,
        description="Main character name",
        example="Finn",
    )
    setting: str = Field(
        default="forest",
        description="Story setting location",
        example="forest",
    )
    tone: str = Field(
        default="dramatic",
        description="Story mood/tone",
        example="dramatic",
    )
    art_style: str = Field(
        default="comic book",
        description="Visual art style for illustrations",
        example="anime",
    )


class PanelSchema(BaseModel):
    """Schema for a single comic panel in the response."""

    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    image_path: str
    image_file_path: str


class ComicResponse(BaseModel):
    """Response schema for the /generate-comic/json endpoint."""

    success: bool
    layout: List[PanelSchema]
    pdf_path: str
    message: str = "Comic generated successfully"
