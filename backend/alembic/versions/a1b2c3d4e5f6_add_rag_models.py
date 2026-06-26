"""Add RAG models

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2026-06-26 22:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '0ebe1f887612'
branch_labels = None
depends_on = None

def upgrade():
    # Create vector extension if it doesn't exist
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create medical_documents table
    op.create_table(
        'medical_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['medical_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('document_chunks')
    op.drop_table('medical_documents')
    op.execute('DROP EXTENSION IF EXISTS vector')
