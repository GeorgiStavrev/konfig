"""Config model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base
from app.db.types import JSONType


class ConfigValueType(str, enum.Enum):
    """Configuration value types."""

    STRING = "string"
    NUMBER = "number"
    SELECT = "select"
    JSON = "json"


class Config(Base):
    """Configuration model."""

    __tablename__ = "configs"
    __table_args__ = (
        UniqueConstraint("namespace_id", "key", name="uq_namespace_config_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace_id = Column(UUID(as_uuid=True), ForeignKey("namespaces.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)  # Encrypted
    value_type = Column(SQLEnum(ConfigValueType), nullable=False, default=ConfigValueType.STRING)
    validation_schema = Column(JSONType, nullable=True)  # JSON schema for validation
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_secret = Column(String(10), default="false", nullable=False)  # Extra flag for sensitive values
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)  # User/Tenant who created

    # Relationships
    namespace = relationship("Namespace", back_populates="configs")
    history = relationship("ConfigHistory", back_populates="config", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Config {self.key}={self.value_type}>"


class ConfigHistory(Base):
    """Configuration history for version tracking."""

    __tablename__ = "config_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("configs.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(Text, nullable=False)  # Encrypted
    version = Column(Integer, nullable=False)
    change_type = Column(String(50), nullable=False)  # create, update, delete
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    changed_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    config = relationship("Config", back_populates="history")

    def __repr__(self) -> str:
        return f"<ConfigHistory {self.config_id} v{self.version}>"
