"""Create the library table if missing and apply lightweight migrations for async classification columns."""

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.db.engine import get_engine


def _migrate_sqlite(connection: Connection) -> None:
    rows = connection.execute(text("PRAGMA table_info(library_items)")).fetchall()
    col_names = {row[1] for row in rows}
    if "classification_status" not in col_names:
        connection.execute(
            text(
                "ALTER TABLE library_items ADD COLUMN classification_status VARCHAR(32) DEFAULT 'completed'"
            )
        )
    if "classification_error" not in col_names:
        connection.execute(text("ALTER TABLE library_items ADD COLUMN classification_error TEXT"))


def _migrate_postgres(connection: Connection) -> None:
    result = connection.execute(
        text(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'library_items'
              AND column_name = 'classification_status'
            """
        )
    )
    if result.fetchone() is None:
        connection.execute(
            text(
                """
                ALTER TABLE library_items
                ADD COLUMN classification_status VARCHAR(32) NOT NULL DEFAULT 'completed'
                """
            )
        )
    result = connection.execute(
        text(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'library_items'
              AND column_name = 'classification_error'
            """
        )
    )
    if result.fetchone() is None:
        connection.execute(text("ALTER TABLE library_items ADD COLUMN classification_error TEXT"))


def initialize_database() -> None:
    engine = get_engine()
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS library_items (
                    id VARCHAR(64) PRIMARY KEY,
                    image_url TEXT NOT NULL,
                    ai_description TEXT NOT NULL,
                    attributes_json TEXT NOT NULL,
                    designer_tags_json TEXT NOT NULL,
                    designer_notes TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    classification_status VARCHAR(32) NOT NULL DEFAULT 'completed',
                    classification_error TEXT
                )
                """
            )
        )

        dialect = connection.dialect.name
        match dialect:
            case "sqlite":
                _migrate_sqlite(connection)
            case "postgresql":
                _migrate_postgres(connection)
            case _:
                pass
