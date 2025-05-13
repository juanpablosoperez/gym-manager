"""add_cuota_mensual_table

Revision ID: f49e8b902ea4
Revises: 
Create Date: 2025-05-13 17:38:31.654527

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f49e8b902ea4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cuota_mensual',
        sa.Column('id_cuota', sa.Integer, primary_key=True),
        sa.Column('monto', sa.Float, nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime, nullable=False),
        sa.Column('activo', sa.Integer, default=1)
    )


def downgrade() -> None:
    op.drop_table('cuota_mensual') 