"""Namespace model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Namespace(Base):
    """Namespace model for organizing configurations."""

    __tablename__ = "namespaces"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_tenant_namespace"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="namespaces")
    configs = relationship(
        "Config", back_populates="namespace", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Namespace {self.name}>"
