"""Migration script to create refresh_tokens table.

Revision ID: 0ebe1f887612
Revises: None
Create Date: 2026-06-26 15:31:49.000000
"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '0ebe1f887612'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'refresh_tokens',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False, index=True),
        sa.Column('user_id', pg.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('token', sa.String(), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

def downgrade():
    op.drop_table('refresh_tokens')
