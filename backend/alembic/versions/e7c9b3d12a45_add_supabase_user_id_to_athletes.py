"""add supabase_user_id to athletes

Revision ID: e7c9b3d12a45
Revises: c8a4f2e9b1d3
Create Date: 2026-05-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e7c9b3d12a45'
down_revision: Union[str, Sequence[str], None] = 'c8a4f2e9b1d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('athletes', sa.Column('supabase_user_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_athletes_supabase_user_id', 'athletes', ['supabase_user_id'])
    op.create_index('ix_athletes_supabase_user_id', 'athletes', ['supabase_user_id'])


def downgrade() -> None:
    op.drop_index('ix_athletes_supabase_user_id', table_name='athletes')
    op.drop_constraint('uq_athletes_supabase_user_id', 'athletes', type_='unique')
    op.drop_column('athletes', 'supabase_user_id')
