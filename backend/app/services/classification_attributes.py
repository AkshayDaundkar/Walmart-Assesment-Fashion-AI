from datetime import UTC, datetime

from app.schemas.library import AiAttributes, LocationContext, TimeContext


def pending_stub_attributes() -> AiAttributes:
    now = datetime.now(UTC)
    return AiAttributes(
        garment_type="Unknown",
        style="Unknown",
        material="Unknown",
        color_palette=[],
        pattern="Unknown",
        season="Unknown",
        occasion="Unknown",
        consumer_profile="Unknown",
        trend_notes=[],
        location_context=LocationContext(continent="Unknown", country="Unknown", city="Unknown"),
        time_context=TimeContext(year=now.year, month=now.month, season="Unknown"),
    )
