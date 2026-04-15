from typing import Literal

from pydantic import BaseModel, Field


class LocationContext(BaseModel):
    continent: str
    country: str
    city: str


class TimeContext(BaseModel):
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    season: str


class AiAttributes(BaseModel):
    garment_type: str
    style: str
    material: str
    color_palette: list[str]
    pattern: str
    season: str
    occasion: str
    consumer_profile: str
    trend_notes: list[str]
    location_context: LocationContext
    time_context: TimeContext


class InspirationImage(BaseModel):
    id: str
    image_url: str
    ai_description: str
    attributes: AiAttributes
    designer_tags: list[str]
    designer_notes: str
    created_at: str
    classification_status: Literal["pending", "completed", "failed"] = "completed"
    classification_error: str | None = None


class FilterFacet(BaseModel):
    key: str
    values: list[str]


class LibraryResponse(BaseModel):
    items: list[InspirationImage]
    facets: list[FilterFacet]


class UploadImageResponse(BaseModel):
    item: InspirationImage


class UpdateAnnotationsRequest(BaseModel):
    designer_tags: list[str] = Field(default_factory=list)
    designer_notes: str = ""


class UpdateAnnotationsResponse(BaseModel):
    item: InspirationImage
