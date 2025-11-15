"""Configuration endpoints."""
from typing import List
from uuid import UUID
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.tenant import Tenant
from app.models.namespace import Namespace
from app.models.config import Config, ConfigHistory, ConfigValueType
from app.schemas.config import ConfigCreate, ConfigUpdate, ConfigResponse, ConfigHistoryResponse
from app.api.dependencies import get_tenant_from_user_or_api_key
from app.core.security import encrypt_value, decrypt_value


router = APIRouter(prefix="/namespaces/{namespace_id}/configs", tags=["configurations"])


def serialize_value(value, value_type: ConfigValueType) -> str:
    """Serialize value to string for storage."""
    if value_type == ConfigValueType.JSON:
        if isinstance(value, str):
            return value
        return json.dumps(value)
    elif value_type == ConfigValueType.NUMBER:
        return str(value)
    else:
        return str(value)


def deserialize_value(value: str, value_type: ConfigValueType):
    """Deserialize value from string."""
    if value_type == ConfigValueType.JSON:
        try:
            return json.loads(value)
        except:
            return value
    elif value_type == ConfigValueType.NUMBER:
        try:
            if "." in value:
                return float(value)
            return int(value)
        except:
            return value
    else:
        return value


async def verify_namespace_access(
    namespace_id: UUID,
    tenant: Tenant,
    db: AsyncSession,
) -> Namespace:
    """Verify that the tenant has access to the namespace."""
    result = await db.execute(
        select(Namespace).where(
            Namespace.id == namespace_id,
            Namespace.tenant_id == tenant.id,
        )
    )
    namespace = result.scalar_one_or_none()

    if not namespace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Namespace not found",
        )

    return namespace


@router.get("", response_model=List[ConfigResponse])
async def list_configs(
    namespace_id: UUID,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> List[Config]:
    """List all configurations in a namespace."""
    # Verify namespace access
    await verify_namespace_access(namespace_id, current_tenant, db)

    # Get configs
    result = await db.execute(
        select(Config).where(Config.namespace_id == namespace_id)
    )
    configs = result.scalars().all()

    # Decrypt values
    for config in configs:
        decrypted_value = decrypt_value(config.value)
        config.value = deserialize_value(decrypted_value, config.value_type)
        config.is_secret = config.is_secret == "true"

    return configs


@router.post("", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    namespace_id: UUID,
    config_data: ConfigCreate,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> Config:
    """Create a new configuration."""
    # Verify namespace access
    await verify_namespace_access(namespace_id, current_tenant, db)

    # Check if config with same key exists
    result = await db.execute(
        select(Config).where(
            Config.namespace_id == namespace_id,
            Config.key == config_data.key,
        )
    )
    existing_config = result.scalar_one_or_none()

    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configuration with this key already exists",
        )

    # Serialize and encrypt value
    serialized_value = serialize_value(config_data.value, config_data.value_type)
    encrypted_value = encrypt_value(serialized_value)

    # Create config
    new_config = Config(
        namespace_id=namespace_id,
        key=config_data.key,
        value=encrypted_value,
        value_type=config_data.value_type,
        validation_schema=config_data.validation_schema.model_dump() if config_data.validation_schema else None,
        description=config_data.description,
        is_secret="true" if config_data.is_secret else "false",
        version=1,
        created_by=current_tenant.id,
    )

    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)

    # Create history entry
    history_entry = ConfigHistory(
        config_id=new_config.id,
        value=encrypted_value,
        version=1,
        change_type="create",
        changed_by=current_tenant.id,
    )
    db.add(history_entry)
    await db.commit()

    # Decrypt for response
    new_config.value = config_data.value
    new_config.is_secret = config_data.is_secret

    return new_config


@router.get("/{config_key}", response_model=ConfigResponse)
async def get_config(
    namespace_id: UUID,
    config_key: str,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> Config:
    """Get a specific configuration."""
    # Verify namespace access
    await verify_namespace_access(namespace_id, current_tenant, db)

    # Get config
    result = await db.execute(
        select(Config).where(
            Config.namespace_id == namespace_id,
            Config.key == config_key,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Decrypt value
    decrypted_value = decrypt_value(config.value)
    config.value = deserialize_value(decrypted_value, config.value_type)
    config.is_secret = config.is_secret == "true"

    return config


@router.put("/{config_key}", response_model=ConfigResponse)
async def update_config(
    namespace_id: UUID,
    config_key: str,
    config_data: ConfigUpdate,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> Config:
    """Update a configuration."""
    # Verify namespace access
    await verify_namespace_access(namespace_id, current_tenant, db)

    # Get config
    result = await db.execute(
        select(Config).where(
            Config.namespace_id == namespace_id,
            Config.key == config_key,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Update fields
    value_changed = False
    if config_data.value is not None:
        value_type = config_data.value_type or config.value_type
        serialized_value = serialize_value(config_data.value, value_type)
        encrypted_value = encrypt_value(serialized_value)
        config.value = encrypted_value
        config.version += 1
        value_changed = True

        # Create history entry
        history_entry = ConfigHistory(
            config_id=config.id,
            value=encrypted_value,
            version=config.version,
            change_type="update",
            changed_by=current_tenant.id,
        )
        db.add(history_entry)

    if config_data.value_type is not None:
        config.value_type = config_data.value_type

    if config_data.validation_schema is not None:
        config.validation_schema = config_data.validation_schema.model_dump()

    if config_data.description is not None:
        config.description = config_data.description

    if config_data.is_secret is not None:
        config.is_secret = "true" if config_data.is_secret else "false"

    await db.commit()
    await db.refresh(config)

    # Decrypt for response
    if value_changed and config_data.value is not None:
        config.value = config_data.value
    else:
        decrypted_value = decrypt_value(config.value)
        config.value = deserialize_value(decrypted_value, config.value_type)

    config.is_secret = config.is_secret == "true"

    return config


@router.delete("/{config_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    namespace_id: UUID,
    config_key: str,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a configuration."""
    # Verify namespace access
    await verify_namespace_access(namespace_id, current_tenant, db)

    # Get config
    result = await db.execute(
        select(Config).where(
            Config.namespace_id == namespace_id,
            Config.key == config_key,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Create history entry before deletion
    history_entry = ConfigHistory(
        config_id=config.id,
        value=config.value,
        version=config.version,
        change_type="delete",
        changed_by=current_tenant.id,
    )
    db.add(history_entry)

    await db.delete(config)
    await db.commit()


@router.get("/{config_key}/history", response_model=List[ConfigHistoryResponse])
async def get_config_history(
    namespace_id: UUID,
    config_key: str,
    current_tenant: Tenant = Depends(get_tenant_from_user_or_api_key),
    db: AsyncSession = Depends(get_db),
) -> List[ConfigHistory]:
    """Get configuration history."""
    # Verify namespace access
    await verify_namespace_access(namespace_id, current_tenant, db)

    # Get config
    result = await db.execute(
        select(Config).where(
            Config.namespace_id == namespace_id,
            Config.key == config_key,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Get history
    result = await db.execute(
        select(ConfigHistory)
        .where(ConfigHistory.config_id == config.id)
        .order_by(ConfigHistory.changed_at.desc())
    )
    history = result.scalars().all()

    # Decrypt values
    for entry in history:
        decrypted_value = decrypt_value(entry.value)
        entry.value = deserialize_value(decrypted_value, config.value_type)

    return history
