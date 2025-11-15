"""initial_migration_with_users_and_api_keys

Revision ID: abc123
Revises:
Create Date: 2025-01-15 00:01:00.000000

This migration creates the initial database schema with proper separation
between tenants, users, and API keys.

Tenants are organizations/companies.
Users are individuals belonging to tenants (with roles: owner, admin, member).
API Keys enable service-to-service authentication.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'abc123'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables with new auth model."""

    # Create tenants table (organization/company only)
    op.create_table(
        'tenants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tenants_name'), 'tenants', ['name'], unique=True)

    # Create users table (individuals belonging to tenants)
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'MEMBER', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)

    # Create api_keys table (service-to-service authentication)
    op.create_table(
        'api_keys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('prefix', sa.String(length=20), nullable=False),
        sa.Column('scopes', sa.Text(), nullable=False, server_default='read'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)
    op.create_index(op.f('ix_api_keys_tenant_id'), 'api_keys', ['tenant_id'], unique=False)

    # Create namespaces table
    op.create_table(
        'namespaces',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_namespaces_tenant_id'), 'namespaces', ['tenant_id'], unique=False)
    op.create_index(
        'ix_namespaces_tenant_id_name',
        'namespaces',
        ['tenant_id', 'name'],
        unique=True
    )

    # Create configs table
    op.create_table(
        'configs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('namespace_id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('value_type', sa.Enum('STRING', 'NUMBER', 'BOOLEAN', 'JSON', name='configvaluetype'), nullable=False),
        sa.Column('validation_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_secret', sa.String(length=10), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_configs_namespace_id'), 'configs', ['namespace_id'], unique=False)
    op.create_index(
        'ix_configs_namespace_id_key',
        'configs',
        ['namespace_id', 'key'],
        unique=True
    )

    # Create config_history table
    op.create_table(
        'config_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('config_id', sa.UUID(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('changed_by', sa.UUID(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['config_id'], ['configs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_history_config_id'), 'config_history', ['config_id'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_config_history_config_id'), table_name='config_history')
    op.drop_table('config_history')

    op.drop_index('ix_configs_namespace_id_key', table_name='configs')
    op.drop_index(op.f('ix_configs_namespace_id'), table_name='configs')
    op.drop_table('configs')

    op.drop_index('ix_namespaces_tenant_id_name', table_name='namespaces')
    op.drop_index(op.f('ix_namespaces_tenant_id'), table_name='namespaces')
    op.drop_table('namespaces')

    op.drop_index(op.f('ix_api_keys_tenant_id'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_key_hash'), table_name='api_keys')
    op.drop_table('api_keys')

    op.drop_index(op.f('ix_users_tenant_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_tenants_name'), table_name='tenants')
    op.drop_table('tenants')

    # Drop enums
    sa.Enum('OWNER', 'ADMIN', 'MEMBER', name='userrole').drop(op.get_bind())
    sa.Enum('STRING', 'NUMBER', 'BOOLEAN', 'JSON', name='configvaluetype').drop(op.get_bind())
