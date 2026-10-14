"""An existing database gains the model's nullable columns without losing its rows.

Happy path: a flashcards table from before `fsrs_card` existed gets the column, and its rows survive.
Unhappy path: a missing NOT NULL column cannot be added automatically, so the migration refuses instead of guessing.
"""

import pytest
from sqlalchemy import Engine, create_engine, inspect, text

from flashcards.core.database import Base, add_missing_columns


def _old_schema(path) -> Engine:
    engine = create_engine(f"sqlite:///{path}")
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE flashcards (id VARCHAR PRIMARY KEY, entry_id VARCHAR NOT NULL, domain VARCHAR NOT NULL, "
                "card_type VARCHAR NOT NULL, front TEXT NOT NULL, back TEXT NOT NULL, tags_json VARCHAR, "
                "stability FLOAT, difficulty FLOAT, repetition_count INTEGER, due_date DATETIME, created_at DATETIME)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO flashcards (id, entry_id, domain, card_type, front, back, repetition_count) "
                "VALUES ('c1', 'e1', 'd', 'term', 'f', 'b', 3)"
            )
        )
    return engine


def test_missing_nullable_column_is_added_and_rows_survive(tmp_path):
    engine = _old_schema(tmp_path / "old.sqlite")

    added = add_missing_columns(engine)

    assert added == ["flashcards.fsrs_card"]
    assert "fsrs_card" in {c["name"] for c in inspect(engine).get_columns("flashcards")}
    with engine.connect() as conn:
        assert conn.execute(text("SELECT repetition_count FROM flashcards WHERE id = 'c1'")).scalar() == 3


def test_migration_is_idempotent(tmp_path):
    engine = _old_schema(tmp_path / "old.sqlite")
    add_missing_columns(engine)

    assert add_missing_columns(engine) == []


def test_a_missing_not_null_column_is_refused(tmp_path, monkeypatch):
    engine = _old_schema(tmp_path / "old.sqlite")
    column = Base.metadata.tables["flashcards"].columns["front"]
    monkeypatch.setattr(column, "nullable", False)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE flashcards RENAME COLUMN front TO front_old"))

    with pytest.raises(RuntimeError, match="NOT NULL"):
        add_missing_columns(engine)
