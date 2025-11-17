"""Namespace schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NamespaceBase(BaseModel):
    """Base namespace schema."""

    name: str = Field(..., min_length=1, max_length=255, pattern="^[a-zA-Z0-9_-]+$")
    description: Optional[str] = None


class NamespaceCreate(NamespaceBase):
    """Schema for creating a namespace."""

    pass


class NamespaceUpdate(BaseModel):
    """Schema for updating a namespace."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, pattern="^[a-zA-Z0-9_-]+$"
    )
    description: Optional[str] = None


class NamespaceResponse(NamespaceBase):
    """Schema for namespace response."""

    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
