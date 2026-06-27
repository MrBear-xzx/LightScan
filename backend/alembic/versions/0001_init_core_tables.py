from alembic import op
import sqlalchemy as sa

revision = '0001_init_core_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'assets',
        sa.Column('asset_id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('asset_type', sa.String(length=32), nullable=False),
        sa.Column('canonical_identifier', sa.String(length=255), nullable=False),
        sa.Column('criticality', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.UniqueConstraint('tenant_id', 'asset_type', 'canonical_identifier', name='uq_asset_identity'),
    )

    op.create_table(
        'scan_tasks',
        sa.Column('task_id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('task_type', sa.String(length=32), nullable=False),
        sa.Column('target_scope', sa.Text(), nullable=False),
        sa.Column('policy_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('worker_id', sa.String(length=64), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'events',
        sa.Column('event_id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('reference_id', sa.String(length=64), nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'findings',
        sa.Column('finding_id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('plugin_id', sa.String(length=64), nullable=False),
        sa.Column('template_or_rule_id', sa.String(length=128), nullable=False),
        sa.Column('vuln_ref', sa.String(length=128), nullable=False),
        sa.Column('severity', sa.String(length=16), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.8'),
        sa.Column('evidence', sa.Text(), nullable=False),
        sa.Column('fingerprint', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'vuln_cases',
        sa.Column('case_id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('normalized_vuln_key', sa.String(length=128), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('state', sa.String(length=32), nullable=False, server_default='new'),
        sa.Column('owner', sa.String(length=128), nullable=True),
        sa.Column('sla_due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'policies',
        sa.Column('policy_id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False, unique=True),
        sa.Column('role', sa.String(length=32), nullable=False, server_default='analyst'),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('policies')
    op.drop_table('vuln_cases')
    op.drop_table('findings')
    op.drop_table('events')
    op.drop_table('scan_tasks')
    op.drop_table('assets')
