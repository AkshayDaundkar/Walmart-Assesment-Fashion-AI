from app.repositories.library_repository import LibraryRepository
from app.schemas.library import InspirationImage
from app.services.classifiers.heuristic import HeuristicImageClassifier
from app.services.library_service import LibraryService


def test_search_matches_description_and_tags(client) -> None:
    classifier = HeuristicImageClassifier()
    _, attributes = classifier.classify_image(image_bytes=b"", filename="jaipur_embroidery_top.jpg")

    repository = LibraryRepository()
    repository.add_item(
        InspirationImage(
            id=classifier.next_id(),
            image_url="https://example.com/a.jpg",
            ai_description="Embroidered neckline top with artisan details",
            attributes=attributes,
            designer_tags=["embroidery"],
            designer_notes="Great neckline",
            created_at="2026-04-01T00:00:00Z",
        )
    )

    service = LibraryService(repository=repository)
    response = service.get_library(query="embroidered neckline")

    assert len(response.items) == 1
    assert response.items[0].attributes.garment_type == "Top"
