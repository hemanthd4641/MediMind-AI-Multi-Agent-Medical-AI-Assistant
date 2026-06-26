{% set revision = revision %}{% set down_revision = down_revision %}{% set create_date = create_date %}
"""{{create_date}}

Revision ID: {{revision}}
Revises: {{down_revision}}
Create Date: {{create_date}}
"""

from alembic import op
import sqlalchemy as sa

{% if upgrade_ops %}
{{ upgrade_ops|indent(4, True) }}
{% else %}
    pass
{% endif %}

{% if downgrade_ops %}
{{ downgrade_ops|indent(4, True) }}
{% else %}
    pass
{% endif %}
