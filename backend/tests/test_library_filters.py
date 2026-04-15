from app.repositories.library_repository import LibraryRepository
from app.schemas.library import InspirationImage
from app.services.classifiers.heuristic import HeuristicImageClassifier
from app.services.library_service import LibraryService


def test_filter_by_location_and_time(client) -> None:
    repository = LibraryRepository()
    classifier = HeuristicImageClassifier()
    _, attributes = classifier.classify_image(image_bytes=b"", filename="tokyo_runway_jacket.jpg")

    repository.add_item(
        InspirationImage(
            id=classifier.next_id(),
            image_url="https://example.com/image.jpg",
            ai_description="Layered jacket from Tokyo fashion week runway.",
            attributes=attributes,
            designer_tags=["tailoring"],
            designer_notes="Check sleeve construction",
            created_at="2026-01-12T08:00:00Z",
        )
    )

    service = LibraryService(repository=repository)
    response = service.get_library(country="Japan", city="Tokyo", time_season=attributes.time_context.season)

    assert len(response.items) == 1
    assert response.items[0].attributes.location_context.city == "Tokyo"
