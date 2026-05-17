"""swap athletes.age for birth_year

Revision ID: c5d6e7f8a9b0
Revises: a2b3c4d5e6f7
Create Date: 2026-05-17 22:00:00.000000

Stores year of birth instead of age so the value doesn't go stale.
Backfills existing rows assuming the age was captured during 2026
(close enough for the validation phase — exact day-of-year doesn't matter
without month/day collected).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, Sequence[str], None] = 'a2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


REFERENCE_YEAR = 2026  # year the migration was authored, used for backfill


def upgrade() -> None:
    op.add_column('athletes', sa.Column('birth_year', sa.Integer(), nullable=True))
    op.execute(
        f"UPDATE athletes SET birth_year = {REFERENCE_YEAR} - age "
        "WHERE age IS NOT NULL AND birth_year IS NULL"
    )
    op.drop_column('athletes', 'age')


def downgrade() -> None:
    op.add_column('athletes', sa.Column('age', sa.Integer(), nullable=True))
    op.execute(
        f"UPDATE athletes SET age = {REFERENCE_YEAR} - birth_year "
        "WHERE birth_year IS NOT NULL AND age IS NULL"
    )
    op.drop_column('athletes', 'birth_year')
