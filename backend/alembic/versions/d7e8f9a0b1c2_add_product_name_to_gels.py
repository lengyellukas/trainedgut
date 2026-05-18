"""add product_name to gels

Revision ID: d7e8f9a0b1c2
Revises: c5d6e7f8a9b0
Create Date: 2026-05-18 10:00:00.000000

Stores the marketing-friendly product name (e.g. "Maurten Gel 100") so the
UI can show what athletes actually search for in shops, instead of just the
internal brand id + size category. Seed scripts populate the values on the
next deploy via UPSERT.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd7e8f9a0b1c2'
down_revision: Union[str, Sequence[str], None] = 'c5d6e7f8a9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('gels', sa.Column('product_name', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('gels', 'product_name')
