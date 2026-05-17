"""add brand and markets columns to gels

Revision ID: f3e7b8c9a012
Revises: d9f0a3b1c2e8
Create Date: 2026-05-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3e7b8c9a012'
down_revision: Union[str, Sequence[str], None] = 'd9f0a3b1c2e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # brand: all existing gels are TrainedGut
    op.add_column(
        'gels',
        sa.Column('brand', sa.String(), nullable=False, server_default='trainedgut'),
    )
    op.create_index('ix_gels_brand', 'gels', ['brand'])

    # markets: existing TrainedGut gels available in all three markets
    op.add_column(
        'gels',
        sa.Column('markets', sa.JSON(), nullable=False, server_default=sa.text("'[\"CH\",\"CZ\",\"SK\"]'::json")),
    )


def downgrade() -> None:
    op.drop_column('gels', 'markets')
    op.drop_index('ix_gels_brand', table_name='gels')
    op.drop_column('gels', 'brand')
