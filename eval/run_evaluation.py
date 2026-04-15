from __future__ import annotations

import json
from pathlib import Path

from app.services.classifier_service import get_image_classifier

EVAL_SET_PATH = Path(__file__).resolve().parent / "labeled_test_set.json"


def evaluate() -> dict[str, float]:
    classifier = get_image_classifier()
    samples = json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))

    tracked_fields = ["garment_type", "style", "material", "occasion", "country"]
    correct_counts: dict[str, int] = {field: 0 for field in tracked_fields}

    for sample in samples:
        _, attributes = classifier.classify_image(image_bytes=b"", filename=sample["file_name"])
        predictions = {
            "garment_type": attributes.garment_type,
            "style": attributes.style,
            "material": attributes.material,
            "occasion": attributes.occasion,
            "country": attributes.location_context.country,
        }
        expected = sample["expected"]

        for field in tracked_fields:
            if predictions[field] == expected[field]:
                correct_counts[field] += 1

    total = len(samples)
    return {field: round(correct / total, 4) for field, correct in correct_counts.items()}


def main() -> None:
    metrics = evaluate()
    print("Evaluation metrics (exact-match accuracy):")
    for field, score in metrics.items():
        print(f"- {field}: {score:.2%}")


if __name__ == "__main__":
    main()
