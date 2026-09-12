"""Add career analysis model

Revision ID: f1234567890a
Revises: 0cce2326c451
Create Date: 2026-09-12 23:37:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1234567890a'
down_revision: Union[str, Sequence[str], None] = '0cce2326c451'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('career_analyses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('strengths', sa.Text(), nullable=True),
    sa.Column('weaknesses', sa.Text(), nullable=True),
    sa.Column('skill_gaps', sa.Text(), nullable=True),
    sa.Column('career_risks', sa.Text(), nullable=True),
    sa.Column('opportunities', sa.Text(), nullable=True),
    sa.Column('recommended_skills', sa.Text(), nullable=True),
    sa.Column('recommended_projects', sa.Text(), nullable=True),
    sa.Column('suitable_roles', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_analyses_id'), 'career_analyses', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_career_analyses_id'), table_name='career_analyses')
    op.drop_table('career_analyses')
