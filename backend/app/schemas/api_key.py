"""API Key schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Friendly name for the API key"
    )
    scopes: str = Field(
        default="read", description="Comma-separated scopes: read, write, admin"
    )
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")


class ApiKeyResponse(BaseModel):
    """Schema for API key response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    prefix: str  # First few characters for identification
    scopes: str
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle string to bool conversion."""
        if hasattr(obj, "is_active") and isinstance(obj.is_active, str):
            obj.is_active = obj.is_active == "true"
        return super().model_validate(obj)


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Schema for API key creation response - includes the actual key (only shown once)."""

    api_key: str = Field(
        ..., description="The actual API key - save this, it won't be shown again!"
    )
