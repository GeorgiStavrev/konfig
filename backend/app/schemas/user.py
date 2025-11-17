"""User schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    role: UserRole = UserRole.MEMBER


class UserRegister(BaseModel):
    """Schema for initial tenant registration with owner user."""

    tenant_name: str = Field(
        ..., min_length=2, max_length=255, description="Organization/company name"
    )
    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    password: Optional[str] = Field(
        None, min_length=8, description="Password must be at least 8 characters"
    )
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle string to bool conversion."""
        if hasattr(obj, "is_active") and isinstance(obj.is_active, str):
            obj.is_active = obj.is_active == "true"
        return super().model_validate(obj)


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse
    tenant_id: UUID
    tenant_name: str
