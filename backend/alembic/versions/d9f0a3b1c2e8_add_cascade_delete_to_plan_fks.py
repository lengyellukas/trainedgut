"""add ON DELETE CASCADE to plan-related foreign keys

Revision ID: d9f0a3b1c2e8
Revises: b5d8e1f2c3a4
Create Date: 2026-05-15 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'd9f0a3b1c2e8'
down_revision: Union[str, Sequence[str], None] = 'b5d8e1f2c3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (constraint_name, table, parent_table, [local_col], [parent_col])
FKS = [
    ('plans_athlete_id_fkey',           'plans',           'athletes', ['athlete_id'], ['id']),
    ('weeks_plan_id_fkey',              'weeks',           'plans',    ['plan_id'],    ['id']),
    ('sessions_week_id_fkey',           'sessions',        'weeks',    ['week_id'],    ['id']),
    ('fueling_windows_session_id_fkey', 'fueling_windows', 'sessions', ['session_id'], ['id']),
    ('feedback_session_id_fkey',        'feedback',        'sessions', ['session_id'], ['id']),
    ('extra_sessions_week_id_fkey',     'extra_sessions',  'weeks',    ['week_id'],    ['id']),
]


def upgrade() -> None:
    for name, table, parent, local_cols, parent_cols in FKS:
        op.drop_constraint(name, table, type_='foreignkey')
        op.create_foreign_key(name, table, parent, local_cols, parent_cols, ondelete='CASCADE')


def downgrade() -> None:
    for name, table, parent, local_cols, parent_cols in FKS:
        op.drop_constraint(name, table, type_='foreignkey')
        op.create_foreign_key(name, table, parent, local_cols, parent_cols)
