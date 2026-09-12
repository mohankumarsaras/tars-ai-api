"""Add learning models

Revision ID: d4444444444d
Revises: c3333333333c
Create Date: 2026-09-13 00:02:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd4444444444d'
down_revision: Union[str, Sequence[str], None] = 'c3333333333c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('knowledge_records', sa.Column('knowledge_type', sa.String(length=50), nullable=True))
    op.create_table('learning_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('knowledge_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['knowledge_id'], ['knowledge_records.id'], ),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_activities_id'), 'learning_activities', ['id'], unique=False)
    
    op.create_table('learning_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.Column('evidence_id', sa.Integer(), nullable=True),
    sa.Column('skill_improvement_delta', sa.Float(), nullable=True),
    sa.Column('next_recommendation', sa.Text(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['learning_activities.id'], ),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
    sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_history_id'), 'learning_history', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_learning_history_id'), table_name='learning_history')
    op.drop_table('learning_history')
    op.drop_index(op.f('ix_learning_activities_id'), table_name='learning_activities')
    op.drop_table('learning_activities')
    op.drop_column('knowledge_records', 'knowledge_type')
