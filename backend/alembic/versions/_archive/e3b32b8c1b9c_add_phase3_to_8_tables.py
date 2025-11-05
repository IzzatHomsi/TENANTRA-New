"""
Add tables for phases 3–8 (notifications, alerting, compliance, agents and visibility).

Revision ID: e3b32b8c1b9c
Revises: d425e646fc13
Create Date: 2025-08-08

This migration creates the database tables required for the
improvements introduced in phases 3 through 8 of the Tenantra
project.  It adds support for alert rules, notifications, per‑user
notification settings, compliance results, agent management,
scheduled scans, scan modules, module results, file and network
visibility, and per‑tenant module overrides.  Each table includes
appropriate foreign keys and auditing timestamps (``created_at`` and
``updated_at``) to align with the ORM models.
"""

from alembic import op
import sqlalchemy as sa

revision = 'e3b32b8c1b9c'
down_revision = 'b5eda931c8e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('name', name='uq_module_name'),
    )
    # Create alert rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('condition', sa.String(), nullable=False),
        sa.Column('threshold', sa.String(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('recipient_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create notification settings table
    op.create_table(
        'notification_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', 'event_type', name='uq_notification_setting'),
    )
    # Create compliance results table
    op.create_table(
        'compliance_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('module', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('details', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('last_checkin', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create scheduled scans table
    op.create_table(
        'scheduled_scans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module', sa.String(length=100), nullable=False),
        sa.Column('schedule', sa.String(), nullable=True),
        sa.Column('next_run', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create scan module results table
    op.create_table(
        'scan_module_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module_id', sa.Integer(), sa.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('details', sa.String(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create file visibility results table
    op.create_table(
        'file_visibility_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('share_name', sa.String(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create network visibility results table
    op.create_table(
        'network_visibility_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('service', sa.String(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # Create tenant modules table
    op.create_table(
        'tenant_modules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module_id', sa.Integer(), sa.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('tenant_id', 'module_id', name='uq_tenant_module'),
    )


def downgrade() -> None:
    # Drop tables in reverse order to respect dependencies
    op.drop_table('tenant_modules')
    op.drop_table('network_visibility_results')
    op.drop_table('file_visibility_results')
    op.drop_table('scan_module_results')
    op.drop_table('scheduled_scans')
    op.drop_table('agents')
    op.drop_table('compliance_results')
    op.drop_table('notification_settings')
    op.drop_table('notifications')
    op.drop_table('alert_rules')
    op.drop_table('modules')