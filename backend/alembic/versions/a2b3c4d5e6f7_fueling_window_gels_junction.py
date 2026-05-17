"""replace fueling_window single-gel columns with junction table

Revision ID: a2b3c4d5e6f7
Revises: f3e7b8c9a012
Create Date: 2026-05-17 16:00:00.000000

Drops the old per-window gel columns (n_small_gels, n_large_gels,
small_gel_id, large_gel_id) and introduces a many-to-many junction table
fueling_window_gels (window_id, gel_id, quantity).

Existing fueling_window rows lose their gel linkages. Plans should be
regenerated after this migration runs.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = 'f3e7b8c9a012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. New junction table
    op.create_table(
        'fueling_window_gels',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('window_id', sa.String(), sa.ForeignKey('fueling_windows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('gel_id', sa.String(), sa.ForeignKey('gels.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
    )
    op.create_index('ix_fueling_window_gels_window_id', 'fueling_window_gels', ['window_id'])

    # 2. Drop the old single-gel columns + FKs
    op.drop_constraint('fueling_windows_small_gel_id_fkey', 'fueling_windows', type_='foreignkey')
    op.drop_constraint('fueling_windows_large_gel_id_fkey', 'fueling_windows', type_='foreignkey')
    op.drop_column('fueling_windows', 'small_gel_id')
    op.drop_column('fueling_windows', 'large_gel_id')
    op.drop_column('fueling_windows', 'n_small_gels')
    op.drop_column('fueling_windows', 'n_large_gels')


def downgrade() -> None:
    op.add_column('fueling_windows', sa.Column('n_large_gels', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('fueling_windows', sa.Column('n_small_gels', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('fueling_windows', sa.Column('large_gel_id', sa.String(), nullable=True))
    op.add_column('fueling_windows', sa.Column('small_gel_id', sa.String(), nullable=True))
    op.create_foreign_key('fueling_windows_small_gel_id_fkey', 'fueling_windows', 'gels', ['small_gel_id'], ['id'])
    op.create_foreign_key('fueling_windows_large_gel_id_fkey', 'fueling_windows', 'gels', ['large_gel_id'], ['id'])

    op.drop_index('ix_fueling_window_gels_window_id', table_name='fueling_window_gels')
    op.drop_table('fueling_window_gels')
