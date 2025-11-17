"""User management endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_user,
    get_tenant_from_user,
    require_role,
)
from app.core.security import get_password_hash
from app.db.base import get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> List[UserResponse]:
    """
    List all users in the current user's tenant.
    Any authenticated user can see their teammates.
    """
    result = await db.execute(
        select(User).where(User.tenant_id == tenant.id).order_by(User.created_at)
    )
    users = result.scalars().all()

    return [UserResponse.model_validate(user) for user in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Add a new user to the tenant.
    Requires ADMIN or OWNER role.
    """
    # Check if user with email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Only owners can create other owners
    if user_data.role == UserRole.OWNER and current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can create other owners",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        tenant_id=tenant.id,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Get details of a specific user.
    Users can only view users in their own tenant.
    """
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update a user.
    - Users can update their own profile (limited fields: full_name, password)
    - Admins can update any user in their tenant
    - Only owners can change roles or activate/deactivate users
    """
    # Fetch the user to update
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Permission checks
    is_self = current_user.id == user_id
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.OWNER]
    is_owner = current_user.role == UserRole.OWNER

    # Self-updates: only allow full_name and password
    if is_self and not is_admin:
        if user_data.role is not None or user_data.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own name and password",
            )

    # Non-admins cannot update other users
    if not is_self and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update this user",
        )

    # Role changes require owner
    if user_data.role is not None and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can change user roles",
        )

    # Cannot change role to/from owner unless you're an owner
    if user_data.role == UserRole.OWNER and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can promote users to owner",
        )

    # Activate/deactivate requires owner
    if user_data.is_active is not None and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can activate/deactivate users",
        )

    # Cannot deactivate yourself
    if is_self and user_data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself",
        )

    # Apply updates
    if user_data.email is not None:
        # Check if email is already taken
        result = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user.email = user_data.email

    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = "true" if user_data.is_active else "false"

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.OWNER)),
    tenant: Tenant = Depends(get_tenant_from_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove a user from the tenant.
    Only owners can delete users.
    Cannot delete yourself.
    """
    # Cannot delete yourself
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself",
        )

    # Fetch the user to delete
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if this is the last owner
    result = await db.execute(
        select(User).where(
            User.tenant_id == tenant.id,
            User.role == UserRole.OWNER,
            User.is_active.is_(True),
        )
    )
    active_owners = result.scalars().all()

    if user.role == UserRole.OWNER and len(active_owners) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last owner. Promote another user to owner first.",
        )

    await db.delete(user)
    await db.commit()
