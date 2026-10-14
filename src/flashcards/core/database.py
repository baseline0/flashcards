from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    """Dependency for FastAPI to inject database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_missing_columns(bind) -> list[str]:
    """Add model columns that an existing table lacks, and return their names.

    `create_all` creates missing tables but never alters existing ones, so a column added to a model would
    otherwise be absent from a database created earlier. Only nullable columns are added, since SQLite cannot
    add a NOT NULL column without a default to a populated table; any other gap raises.
    """
    from sqlalchemy import inspect, text

    added = []
    inspector = inspect(bind)
    for table in Base.metadata.sorted_tables:
        if not inspector.has_table(table.name):
            continue
        existing = {column["name"] for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing:
                continue
            if not column.nullable:
                raise RuntimeError(f"{table.name}.{column.name} is NOT NULL and cannot be added automatically")
            column_type = column.type.compile(dialect=bind.dialect)
            with bind.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {column_type}'))
            added.append(f"{table.name}.{column.name}")
    return added


def init_db() -> None:
    """Initialize database schema, then add any columns an older database lacks."""
    Base.metadata.create_all(bind=engine)
    add_missing_columns(engine)
