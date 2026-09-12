"""Add forecast models

Revision ID: b2222222222b
Revises: a1111111111a
Create Date: 2026-09-12 23:48:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2222222222b'
down_revision: Union[str, Sequence[str], None] = 'a1111111111a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('forecast_scenarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('query', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forecast_scenarios_id'), 'forecast_scenarios', ['id'], unique=False)

    op.create_table('forecast_paths',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=False),
    sa.Column('path_name', sa.String(length=255), nullable=False),
    sa.Column('current_skill_fit', sa.Text(), nullable=True),
    sa.Column('experience_leverage', sa.Text(), nullable=True),
    sa.Column('skill_gap', sa.Text(), nullable=True),
    sa.Column('learning_effort', sa.Text(), nullable=True),
    sa.Column('transition_difficulty', sa.Text(), nullable=True),
    sa.Column('market_relevance', sa.Text(), nullable=True),
    sa.Column('growth_potential', sa.Text(), nullable=True),
    sa.Column('summary_assessment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['scenario_id'], ['forecast_scenarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forecast_paths_id'), 'forecast_paths', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_forecast_paths_id'), table_name='forecast_paths')
    op.drop_table('forecast_paths')
    op.drop_index(op.f('ix_forecast_scenarios_id'), table_name='forecast_scenarios')
    op.drop_table('forecast_scenarios')
