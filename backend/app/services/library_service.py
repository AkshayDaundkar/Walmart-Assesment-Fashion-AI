from app.repositories.library_repository import LibraryRepository
from app.schemas.library import InspirationImage, LibraryResponse


class LibraryService:
    """Domain layer: apply text search and facet filters over stored library rows."""
    def __init__(self, repository: LibraryRepository) -> None:
        self._repository = repository

    def get_library(
        self,
        *,
        query: str | None = None,
        garment_type: str | None = None,
        style: str | None = None,
        material: str | None = None,
        occasion: str | None = None,
        consumer_profile: str | None = None,
        continent: str | None = None,
        country: str | None = None,
        city: str | None = None,
        time_season: str | None = None,
        year: int | None = None,
        month: int | None = None,
        pattern: str | None = None,
        garment_season: str | None = None,
        color_palette: str | None = None,
        trend_notes: str | None = None,
    ) -> LibraryResponse:
        items = self._repository.list_items()

        if query:
            query_lower = query.strip().lower()
            items = [
                item
                for item in items
                if query_lower in item.ai_description.lower()
                or query_lower in item.attributes.garment_type.lower()
                or query_lower in item.attributes.style.lower()
                or query_lower in item.attributes.material.lower()
                or query_lower in item.attributes.location_context.city.lower()
                or any(query_lower in tag.lower() for tag in item.designer_tags)
                or query_lower in item.designer_notes.lower()
                or any(query_lower in note.lower() for note in item.attributes.trend_notes)
            ]

        def equals(value: str, target: str | None) -> bool:
            return target is None or value.lower() == target.lower()

        def color_matches(item_palette: list[str], target: str | None) -> bool:
            if target is None:
                return True
            t = target.lower()
            return any(c.lower() == t for c in item_palette)

        def trend_matches(item_notes: list[str], target: str | None) -> bool:
            if target is None:
                return True
            t = target.lower()
            return any(n.lower() == t for n in item_notes)

        items = [
            item
            for item in items
            if equals(item.attributes.garment_type, garment_type)
            and equals(item.attributes.style, style)
            and equals(item.attributes.material, material)
            and equals(item.attributes.occasion, occasion)
            and equals(item.attributes.consumer_profile, consumer_profile)
            and equals(item.attributes.location_context.continent, continent)
            and equals(item.attributes.location_context.country, country)
            and equals(item.attributes.location_context.city, city)
            and equals(item.attributes.time_context.season, time_season)
            and (year is None or item.attributes.time_context.year == year)
            and (month is None or item.attributes.time_context.month == month)
            and equals(item.attributes.pattern, pattern)
            and equals(item.attributes.season, garment_season)
            and color_matches(item.attributes.color_palette, color_palette)
            and trend_matches(item.attributes.trend_notes, trend_notes)
        ]

        return LibraryResponse(items=items, facets=self._repository.build_facets(items))

    def add_item(self, item: InspirationImage) -> InspirationImage:
        return self._repository.add_item(item)

    def get_item(self, item_id: str) -> InspirationImage | None:
        return self._repository.get_by_id(item_id)

    def update_annotations(
        self, item_id: str, designer_tags: list[str], designer_notes: str
    ) -> InspirationImage | None:
        return self._repository.update_annotations(item_id, designer_tags, designer_notes)
