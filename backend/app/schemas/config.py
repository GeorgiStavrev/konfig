"""Configuration schemas."""
from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import json

from app.models.config import ConfigValueType


class ValidationSchema(BaseModel):
    """Validation schema for config values."""

    # For string type
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # regex pattern

    # For number type
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    # For select type
    options: Optional[List[str]] = None

    # For json type
    json_schema: Optional[Dict[str, Any]] = None


class ConfigBase(BaseModel):
    """Base config schema."""

    key: str = Field(..., min_length=1, max_length=255, pattern="^[a-zA-Z0-9_.-]+$")
    value: Any
    value_type: ConfigValueType
    validation_schema: Optional[ValidationSchema] = None
    description: Optional[str] = None
    is_secret: bool = False

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: Any, info) -> Any:
        """Validate value based on type."""
        if "value_type" not in info.data:
            return v

        value_type = info.data["value_type"]

        if value_type == ConfigValueType.STRING:
            if not isinstance(v, str):
                raise ValueError("Value must be a string")

        elif value_type == ConfigValueType.NUMBER:
            if not isinstance(v, (int, float)):
                raise ValueError("Value must be a number")

        elif value_type == ConfigValueType.SELECT:
            if not isinstance(v, str):
                raise ValueError("Value must be a string for select type")
            # Additional validation against options will be done in service layer

        elif value_type == ConfigValueType.JSON:
            if isinstance(v, str):
                try:
                    json.loads(v)
                except json.JSONDecodeError:
                    raise ValueError("Value must be valid JSON")
            elif not isinstance(v, (dict, list)):
                raise ValueError("Value must be a JSON object or array")

        return v


class ConfigCreate(ConfigBase):
    """Schema for creating a config."""

    pass


class ConfigUpdate(BaseModel):
    """Schema for updating a config."""

    value: Optional[Any] = None
    value_type: Optional[ConfigValueType] = None
    validation_schema: Optional[ValidationSchema] = None
    description: Optional[str] = None
    is_secret: Optional[bool] = None


class ConfigResponse(BaseModel):
    """Schema for config response."""

    id: UUID
    namespace_id: UUID
    key: str
    value: Any  # Decrypted value
    value_type: ConfigValueType
    validation_schema: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_secret: bool
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigHistoryResponse(BaseModel):
    """Schema for config history response."""

    id: UUID
    config_id: UUID
    value: Any
    version: int
    change_type: str
    changed_at: datetime
    changed_by: Optional[UUID] = None

    class Config:
        from_attributes = True
