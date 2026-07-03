"""remove pgvector

Revision ID: 1657d89b4a13
Revises: a1b2c3d4e5f6
Create Date: 2026-06-27 00:38:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1657d89b4a13'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop embedding column
    op.drop_column('document_chunks', 'embedding')
    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector;')

def downgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    op.add_column('document_chunks', sa.Column('embedding', sa.Text(), nullable=True))
