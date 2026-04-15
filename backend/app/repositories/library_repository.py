"""SQLAlchemy-backed persistence for library items, facets, and annotation updates."""

import json
from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from sqlalchemy import text

from app.db.engine import get_engine
from app.schemas.library import FilterFacet, InspirationImage


class LibraryRepository:
    def list_items(self) -> list[InspirationImage]:
        engine = get_engine()
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT id, image_url, ai_description, attributes_json, designer_tags_json,
                           designer_notes, created_at, classification_status, classification_error
                    FROM library_items
                    ORDER BY created_at DESC
                    """
                )
            ).mappings().all()

        return [self._row_to_model(row) for row in rows]

    def get_by_id(self, item_id: str) -> InspirationImage | None:
        engine = get_engine()
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT id, image_url, ai_description, attributes_json, designer_tags_json,
                           designer_notes, created_at, classification_status, classification_error
                    FROM library_items
                    WHERE id = :id
                    """
                ),
                {"id": item_id},
            ).mappings().fetchone()

        return self._row_to_model(row) if row else None

    def add_item(self, item: InspirationImage) -> InspirationImage:
        engine = get_engine()
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO library_items (
                        id, image_url, ai_description, attributes_json, designer_tags_json,
                        designer_notes, created_at, classification_status, classification_error
                    ) VALUES (
                        :id, :image_url, :ai_description, :attributes_json, :designer_tags_json,
                        :designer_notes, :created_at, :classification_status, :classification_error
                    )
                    """
                ),
                {
                    "id": item.id,
                    "image_url": item.image_url,
                    "ai_description": item.ai_description,
                    "attributes_json": item.attributes.model_dump_json(),
                    "designer_tags_json": json.dumps(item.designer_tags),
                    "designer_notes": item.designer_notes,
                    "created_at": item.created_at,
                    "classification_status": item.classification_status,
                    "classification_error": item.classification_error,
                },
            )

        return item

    def update_classification(
        self,
        item_id: str,
        *,
        ai_description: str,
        attributes_json: str,
        status: str,
        error: str | None,
    ) -> InspirationImage | None:
        engine = get_engine()
        with engine.begin() as connection:
            cursor = connection.execute(
                text(
                    """
                    UPDATE library_items
                    SET ai_description = :ai_description,
                        attributes_json = :attributes_json,
                        classification_status = :classification_status,
                        classification_error = :classification_error
                    WHERE id = :id
                    """
                ),
                {
                    "id": item_id,
                    "ai_description": ai_description,
                    "attributes_json": attributes_json,
                    "classification_status": status,
                    "classification_error": error,
                },
            )
            if cursor.rowcount == 0:
                return None

            row = connection.execute(
                text(
                    """
                    SELECT id, image_url, ai_description, attributes_json, designer_tags_json,
                           designer_notes, created_at, classification_status, classification_error
                    FROM library_items
                    WHERE id = :id
                    """
                ),
                {"id": item_id},
            ).mappings().fetchone()

        return self._row_to_model(row) if row else None

    def update_annotations(self, item_id: str, designer_tags: list[str], designer_notes: str) -> InspirationImage | None:
        engine = get_engine()
        with engine.begin() as connection:
            cursor = connection.execute(
                text(
                    """
                    UPDATE library_items
                    SET designer_tags_json = :designer_tags_json, designer_notes = :designer_notes
                    WHERE id = :id
                    """
                ),
                {
                    "designer_tags_json": json.dumps(designer_tags),
                    "designer_notes": designer_notes,
                    "id": item_id,
                },
            )
            if cursor.rowcount == 0:
                return None

            row = connection.execute(
                text(
                    """
                    SELECT id, image_url, ai_description, attributes_json, designer_tags_json,
                           designer_notes, created_at, classification_status, classification_error
                    FROM library_items
                    WHERE id = :id
                    """
                ),
                {"id": item_id},
            ).mappings().fetchone()

        return self._row_to_model(row) if row else None

    def build_facets(self, items: list[InspirationImage]) -> list[FilterFacet]:
        buckets: dict[str, set[str]] = defaultdict(set)

        for item in items:
            if item.classification_status != "completed":
                continue
            buckets["garment_type"].add(item.attributes.garment_type)
            buckets["style"].add(item.attributes.style)
            buckets["material"].add(item.attributes.material)
            buckets["pattern"].add(item.attributes.pattern)
            buckets["garment_season"].add(item.attributes.season)
            buckets["occasion"].add(item.attributes.occasion)
            buckets["consumer_profile"].add(item.attributes.consumer_profile)
            buckets["continent"].add(item.attributes.location_context.continent)
            buckets["country"].add(item.attributes.location_context.country)
            buckets["city"].add(item.attributes.location_context.city)
            buckets["time_season"].add(item.attributes.time_context.season)
            buckets["year"].add(str(item.attributes.time_context.year))
            buckets["month"].add(str(item.attributes.time_context.month))
            for color in item.attributes.color_palette:
                buckets["color_palette"].add(color)
            for note in item.attributes.trend_notes:
                buckets["trend_notes"].add(note)

        return [
            FilterFacet(key=key, values=sorted(values))
            for key, values in sorted(buckets.items())
            if values
        ]

    @staticmethod
    def _row_to_model(row: Mapping[str, Any]) -> InspirationImage:
        mapping = dict(row)
        mapping["attributes"] = json.loads(mapping.pop("attributes_json"))
        mapping["designer_tags"] = json.loads(mapping.pop("designer_tags_json"))
        status = mapping.get("classification_status") or "completed"
        mapping["classification_status"] = status
        return InspirationImage.model_validate(mapping)
