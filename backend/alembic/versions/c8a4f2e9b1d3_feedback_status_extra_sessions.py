"""add feedback status and extra_sessions table

Revision ID: c8a4f2e9b1d3
Revises: a135208cbf74
Create Date: 2026-05-14 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c8a4f2e9b1d3'
down_revision: Union[str, Sequence[str], None] = 'a135208cbf74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add status column to feedback (existing rows default to 'completed')
    op.add_column(
        'feedback',
        sa.Column('status', sa.String(), nullable=False, server_default='completed'),
    )

    # 2. Make completion-specific fields nullable (skipped sessions leave them empty)
    op.alter_column('feedback', 'consumed_vs_plan', existing_type=sa.String(), nullable=True)
    op.alter_column('feedback', 'consumed_ratio',   existing_type=sa.Float(),  nullable=True)
    op.alter_column('feedback', 'gi_scale',         existing_type=sa.Integer(), nullable=True)

    # 3. Create extra_sessions table for unplanned sessions the athlete completed
    op.create_table(
        'extra_sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('week_id', sa.String(), sa.ForeignKey('weeks.id'), nullable=False),
        sa.Column('duration_option', sa.String(), nullable=False),
        sa.Column('n_small_gels_consumed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('n_large_gels_consumed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('gi_scale', sa.Integer(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('extra_sessions')
    op.alter_column('feedback', 'gi_scale',         existing_type=sa.Integer(), nullable=False)
    op.alter_column('feedback', 'consumed_ratio',   existing_type=sa.Float(),   nullable=False)
    op.alter_column('feedback', 'consumed_vs_plan', existing_type=sa.String(),  nullable=False)
    op.drop_column('feedback', 'status')
