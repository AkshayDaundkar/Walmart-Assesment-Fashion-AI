from app.services.model_output_parser import parse_model_output


def test_parse_model_output_returns_structured_attributes() -> None:
    raw = {
        "garment_type": "Skirt",
        "style": "Bohemian",
        "material": "Linen",
        "color_palette": ["Ivory", "Sage"],
        "pattern": "Floral",
        "season": "Summer",
        "occasion": "Resort",
        "consumer_profile": "Women 25-40",
        "trend_notes": ["Soft volume"],
        "location_context": {"continent": "Europe", "country": "Spain", "city": "Ibiza"},
        "time_context": {"year": 2026, "month": 6, "season": "Summer"},
    }

    parsed = parse_model_output(raw)

    assert parsed.garment_type == "Skirt"
    assert parsed.location_context.country == "Spain"
