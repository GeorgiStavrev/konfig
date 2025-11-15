"""Tenant schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class TenantBase(BaseModel):
    """Base tenant schema."""

    name: str = Field(..., min_length=2, max_length=255)


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    """Schema for tenant response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle string to bool conversion."""
        if hasattr(obj, 'is_active') and isinstance(obj.is_active, str):
            obj.is_active = obj.is_active == "true"
        return super().model_validate(obj)
