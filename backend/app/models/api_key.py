"""API Key model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ApiKey(Base):
    """API Key model - for service-to-service authentication."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)  # Friendly name for the key
    key_hash = Column(
        String(255), unique=True, nullable=False, index=True
    )  # Hashed API key
    prefix = Column(
        String(20), nullable=False
    )  # First few chars for identification (e.g., "sk_test_abc...")
    scopes = Column(
        Text, nullable=False, default="read"
    )  # Comma-separated: read, write, admin
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    created_by = Column(UUID(as_uuid=True), nullable=True)  # User who created it
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<ApiKey {self.name} ({self.prefix})>"
