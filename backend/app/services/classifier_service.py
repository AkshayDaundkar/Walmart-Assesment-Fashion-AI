from app.core.config import settings
from app.services.classifiers.base import ImageClassifier
from app.services.classifiers.heuristic import HeuristicImageClassifier


def get_image_classifier() -> ImageClassifier:
    match settings.classifier_backend:
        case "heuristic":
            return HeuristicImageClassifier()
        case "openai":
            from app.services.classifiers.openai_vision import OpenAiVisionClassifier

            return OpenAiVisionClassifier()
