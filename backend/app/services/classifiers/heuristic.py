from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.schemas.library import AiAttributes
from app.services.model_output_parser import parse_model_output


def _contains_any(text: str, values: tuple[str, ...]) -> bool:
    return any(value in text for value in values)


class HeuristicImageClassifier:
    """Deterministic classifier from filename hints; no external API."""

    def classify_image(self, *, image_bytes: bytes, filename: str) -> tuple[str, AiAttributes]:
        _ = image_bytes
        lowered = Path(filename).stem.lower()
        now = datetime.now(UTC)

        garment_type = "Dress"
        if _contains_any(lowered, ("jacket", "coat", "outerwear")):
            garment_type = "Jacket"
        elif _contains_any(lowered, ("top", "tee", "shirt", "blouse")):
            garment_type = "Top"
        elif _contains_any(lowered, ("pant", "trouser", "jean")):
            garment_type = "Bottom"
        elif _contains_any(lowered, ("skirt",)):
            garment_type = "Skirt"

        style = "Contemporary street"
        if _contains_any(lowered, ("boho", "bohemian")):
            style = "Bohemian"
        elif _contains_any(lowered, ("ethnic", "artisan")):
            style = "Contemporary ethnic"

        material = "Cotton blend"
        if _contains_any(lowered, ("linen",)):
            material = "Linen"
        elif _contains_any(lowered, ("denim",)):
            material = "Denim"
        elif _contains_any(lowered, ("wool",)):
            material = "Wool"

        country = "France"
        city = "Paris"
        continent = "Europe"
        if _contains_any(lowered, ("tokyo", "japan")):
            country, city, continent = "Japan", "Tokyo", "Asia"
        elif _contains_any(lowered, ("jaipur", "india")):
            country, city, continent = "India", "Jaipur", "Asia"
        elif _contains_any(lowered, ("milan", "italy")):
            country, city, continent = "Italy", "Milan", "Europe"

        occasion = "Daywear"
        if _contains_any(lowered, ("runway",)):
            occasion = "Runway"
        elif _contains_any(lowered, ("resort",)):
            occasion = "Resort"

        mock_output = {
            "garment_type": garment_type,
            "style": style,
            "material": material,
            "color_palette": ["Black", "Sand"],
            "pattern": "Solid",
            "season": "All season",
            "occasion": occasion,
            "consumer_profile": "Urban women 20-35",
            "trend_notes": ["Minimal utility", "Soft tailoring"],
            "location_context": {
                "continent": continent,
                "country": country,
                "city": city,
            },
            "time_context": {
                "year": now.year,
                "month": now.month,
                "season": "Spring" if now.month in {3, 4, 5} else "Other",
            },
        }

        attributes = parse_model_output(mock_output)
        description = (
            f"{attributes.style} {attributes.garment_type.lower()} in {attributes.material.lower()} "
            f"captured in {attributes.location_context.city}, {attributes.location_context.country}."
        )
        return description, attributes

    def next_id(self) -> str:
        return f"img_{uuid4().hex[:12]}"
