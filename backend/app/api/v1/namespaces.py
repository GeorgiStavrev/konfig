"""Namespace endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.tenant import Tenant
from app.models.namespace import Namespace
from app.schemas.namespace import NamespaceCreate, NamespaceUpdate, NamespaceResponse
from app.api.dependencies import get_tenant_from_user_or_api_key


router = APIRouter(prefix="/namespaces", tags=["namespaces"])


@router.get("", response_model=List[NamespaceResponse])
async def list_namespaces(
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> List[Namespace]:
    """List all namespaces for the current tenant."""
    result = await db.execute(
        select(Namespace).where(Namespace.tenant_id == current_tenant.id)
    )
    namespaces = result.scalars().all()
    return namespaces


@router.post("", response_model=NamespaceResponse, status_code=status.HTTP_201_CREATED)
async def create_namespace(
    namespace_data: NamespaceCreate,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> Namespace:
    """Create a new namespace."""
    # Check if namespace with same name exists for this tenant
    result = await db.execute(
        select(Namespace).where(
            Namespace.tenant_id == current_tenant.id,
            Namespace.name == namespace_data.name,
        )
    )
    existing_namespace = result.scalar_one_or_none()

    if existing_namespace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Namespace with this name already exists",
        )

    # Create new namespace
    new_namespace = Namespace(
        tenant_id=current_tenant.id,
        name=namespace_data.name,
        description=namespace_data.description,
    )

    db.add(new_namespace)
    await db.commit()
    await db.refresh(new_namespace)

    return new_namespace


@router.get("/{namespace_id}", response_model=NamespaceResponse)
async def get_namespace(
    namespace_id: UUID,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> Namespace:
    """Get a specific namespace."""
    result = await db.execute(
        select(Namespace).where(
            Namespace.id == namespace_id,
            Namespace.tenant_id == current_tenant.id,
        )
    )
    namespace = result.scalar_one_or_none()

    if not namespace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Namespace not found",
        )

    return namespace


@router.put("/{namespace_id}", response_model=NamespaceResponse)
async def update_namespace(
    namespace_id: UUID,
    namespace_data: NamespaceUpdate,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> Namespace:
    """Update a namespace."""
    result = await db.execute(
        select(Namespace).where(
            Namespace.id == namespace_id,
            Namespace.tenant_id == current_tenant.id,
        )
    )
    namespace = result.scalar_one_or_none()

    if not namespace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Namespace not found",
        )

    # Update fields
    if namespace_data.name is not None:
        # Check if new name conflicts
        result = await db.execute(
            select(Namespace).where(
                Namespace.tenant_id == current_tenant.id,
                Namespace.name == namespace_data.name,
                Namespace.id != namespace_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Namespace with this name already exists",
            )
        namespace.name = namespace_data.name

    if namespace_data.description is not None:
        namespace.description = namespace_data.description

    await db.commit()
    await db.refresh(namespace)

    return namespace


@router.delete("/{namespace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_namespace(
    namespace_id: UUID,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a namespace."""
    result = await db.execute(
        select(Namespace).where(
            Namespace.id == namespace_id,
            Namespace.tenant_id == current_tenant.id,
        )
    )
    namespace = result.scalar_one_or_none()

    if not namespace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Namespace not found",
        )

    await db.delete(namespace)
    await db.commit()
