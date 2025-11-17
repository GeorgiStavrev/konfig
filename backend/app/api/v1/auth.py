"""Authentication endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.base import get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Register a new tenant with an owner user.
    This creates both a tenant (organization) and the first user (owner).
    """
    # Check if user with email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if tenant with name already exists
    result = await db.execute(
        select(Tenant).where(Tenant.name == user_data.tenant_name)
    )
    existing_tenant = result.scalar_one_or_none()

    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant name already taken",
        )

    # Create new tenant
    new_tenant = Tenant(
        name=user_data.tenant_name,
    )

    db.add(new_tenant)
    await db.flush()  # Flush to get tenant ID

    # Create owner user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        tenant_id=new_tenant.id,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.OWNER,  # First user is always owner
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    await db.refresh(new_tenant)

    # Create tokens
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    # Build response
    user_response = UserResponse.model_validate(new_user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=user_response,
        tenant_id=new_tenant.id,
        tenant_name=new_tenant.name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login user and get access token."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Get tenant
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is inactive",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Build response
    user_response = UserResponse.model_validate(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=user_response,
        tenant_id=tenant.id,
        tenant_name=tenant.name,
    )
