"""Add global_search FTS5 table

Revision ID: 591c7eb134d8
Revises: e0a1064d0b13
Create Date: 2026-09-12 23:23:58.629029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '591c7eb134d8'
down_revision: Union[str, Sequence[str], None] = 'e0a1064d0b13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS global_search USING fts5(
            entity_id UNINDEXED, 
            entity_type, 
            title, 
            content, 
            verification_status, 
            source
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS global_search;")
