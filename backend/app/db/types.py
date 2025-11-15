"""Custom SQLAlchemy types for cross-database compatibility."""
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import TypeDecorator


class JSONType(TypeDecorator):
    """
    JSON type that works across different databases.

    Uses JSONB for PostgreSQL and JSON for other databases like SQLite.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load the appropriate type based on the database dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        """Process the value before binding to the database."""
        return value

    def process_result_value(self, value, dialect):
        """Process the value after loading from the database."""
        return value
