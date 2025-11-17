"""API Key management endpoints."""
import secrets
from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse
from app.api.dependencies import (
    get_current_user,
    get_tenant_from_user,
    require_role,
)
from app.core.security import get_password_hash


router = APIRouter(prefix="/api-keys", tags=["api-keys"])


def generate_api_key() -> str:
    """
    Generate a secure random API key.
    Format: konfig_<32 random chars>
    """
    random_part = secrets.token_urlsafe(32)
    return f"konfig_{random_part}"


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> List[ApiKeyResponse]:
    """
    List all API keys for the tenant.
    Requires ADMIN or OWNER role.
    """
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.tenant_id == tenant.id)
        .order_by(ApiKey.created_at.desc())
    )
    api_keys = result.scalars().all()

    return [ApiKeyResponse.model_validate(key) for key in api_keys]


@router.post("", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> ApiKeyCreatedResponse:
    """
    Create a new API key for the tenant.
    Requires ADMIN or OWNER role.

    The API key is only shown once - make sure to save it!
    """
    # Generate API key
    api_key = generate_api_key()

    # Extract prefix (first 12 characters for identification)
    prefix = api_key[:12]

    # Hash the full API key for storage
    key_hash = get_password_hash(api_key)

    # Create API key record
    new_api_key = ApiKey(
        tenant_id=tenant.id,
        name=key_data.name,
        key_hash=key_hash,
        prefix=prefix,
        scopes=key_data.scopes,
        expires_at=key_data.expires_at,
        created_by=current_user.id,
    )

    db.add(new_api_key)
    await db.commit()
    await db.refresh(new_api_key)

    # Build response including the actual API key (only shown once)
    # We need to manually construct the response dict to include the api_key field
    response_data = {
        "id": new_api_key.id,
        "tenant_id": new_api_key.tenant_id,
        "name": new_api_key.name,
        "prefix": new_api_key.prefix,
        "scopes": new_api_key.scopes,
        "is_active": new_api_key.is_active,
        "last_used_at": new_api_key.last_used_at,
        "expires_at": new_api_key.expires_at,
        "created_at": new_api_key.created_at,
        "api_key": api_key,  # Include the full API key (only shown once)
    }

    return ApiKeyCreatedResponse(**response_data)


@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> ApiKeyResponse:
    """
    Get details of a specific API key.
    Requires ADMIN or OWNER role.
    """
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.tenant_id == tenant.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return ApiKeyResponse.model_validate(api_key)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Revoke (delete) an API key.
    Requires ADMIN or OWNER role.
    """
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.tenant_id == tenant.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await db.delete(api_key)
    await db.commit()
