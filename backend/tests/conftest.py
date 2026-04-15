from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.engine import reset_engine
from app.db.init_db import initialize_database
from app.main import app


@pytest.fixture
def client(tmp_path) -> Generator[TestClient, None, None]:
    original_database_url = settings.database_url
    original_storage_root = settings.storage_root
    original_seed = settings.seed_demo_data
    original_execution = settings.classification_execution
    original_public_base = settings.public_assets_base_url
    original_classifier = settings.classifier_backend

    db_file = tmp_path / "fashion-test-data" / "library.db"
    db_file.parent.mkdir(parents=True, exist_ok=True)
    settings.database_url = f"sqlite:///{db_file.resolve().as_posix()}"
    settings.storage_root = str(tmp_path / "fashion-test-data" / "storage")
    settings.seed_demo_data = False
    settings.classification_execution = "sync"
    settings.public_assets_base_url = "http://testserver"
    # Avoid live OpenAI calls (rate limits / cost) when developer .env uses openai.
    settings.classifier_backend = "heuristic"

    reset_engine()
    initialize_database()

    with TestClient(app) as test_client:
        yield test_client

    reset_engine()
    settings.database_url = original_database_url
    settings.storage_root = original_storage_root
    settings.seed_demo_data = original_seed
    settings.classification_execution = original_execution
    settings.public_assets_base_url = original_public_base
    settings.classifier_backend = original_classifier
