"""Pydantic schemas."""
from app.schemas.tenant import (
    TenantBase,
    TenantUpdate,
    TenantResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRegister,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
)
from app.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyCreatedResponse,
)
from app.schemas.namespace import (
    NamespaceBase,
    NamespaceCreate,
    NamespaceUpdate,
    NamespaceResponse,
)
from app.schemas.config import (
    ConfigBase,
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
    ConfigHistoryResponse,
    ValidationSchema,
)

__all__ = [
    # Tenant
    "TenantBase",
    "TenantUpdate",
    "TenantResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    # API Key
    "ApiKeyCreate",
    "ApiKeyResponse",
    "ApiKeyCreatedResponse",
    # Namespace
    "NamespaceBase",
    "NamespaceCreate",
    "NamespaceUpdate",
    "NamespaceResponse",
    # Config
    "ConfigBase",
    "ConfigCreate",
    "ConfigUpdate",
    "ConfigResponse",
    "ConfigHistoryResponse",
    "ValidationSchema",
]
