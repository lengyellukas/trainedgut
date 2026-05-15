"""add is_consolidation to weeks

Revision ID: b5d8e1f2c3a4
Revises: e7c9b3d12a45
Create Date: 2026-05-15 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b5d8e1f2c3a4'
down_revision: Union[str, Sequence[str], None] = 'e7c9b3d12a45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'weeks',
        sa.Column('is_consolidation', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade() -> None:
    op.drop_column('weeks', 'is_consolidation')
