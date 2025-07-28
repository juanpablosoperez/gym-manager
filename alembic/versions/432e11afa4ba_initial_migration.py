"""initial_migration

Revision ID: 432e11afa4ba
Revises: 
Create Date: 2025-06-17 18:00:46.436000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '432e11afa4ba'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla rutinas
    op.create_table('rutinas',
        sa.Column('id_rutina', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('documento_rutina', sa.LargeBinary(length=16777216), nullable=True),
        sa.Column('nivel_dificultad', sa.String(length=20), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_horario', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id_rutina')
    )

    # Crear tabla miembros
    op.create_table('miembros',
        sa.Column('id_miembro', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('apellido', sa.String(length=50), nullable=False),
        sa.Column('documento', sa.String(length=20), nullable=False),
        sa.Column('fecha_nacimiento', sa.Date(), nullable=False),
        sa.Column('genero', sa.String(length=10), nullable=False),
        sa.Column('correo_electronico', sa.String(length=100), nullable=False),
        sa.Column('estado', sa.Boolean(), nullable=False),
        sa.Column('tipo_membresia', sa.String(length=20), nullable=False),
        sa.Column('direccion', sa.String(length=200), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=False),
        sa.Column('informacion_medica', sa.Text(), nullable=True),
        sa.Column('id_rutina', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_rutina'], ['rutinas.id_rutina'], ),
        sa.PrimaryKeyConstraint('id_miembro'),
        sa.UniqueConstraint('documento'),
        sa.UniqueConstraint('correo_electronico')
    )

    # Crear tabla metodos_pago
    op.create_table('metodos_pago',
        sa.Column('id_metodo_pago', sa.Integer(), nullable=False),
        sa.Column('descripcion', sa.String(length=50), nullable=False),
        sa.Column('estado', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id_metodo_pago')
    )

    # Crear tabla pagos
    op.create_table('pagos',
        sa.Column('id_pago', sa.Integer(), nullable=False),
        sa.Column('fecha_pago', sa.DateTime(), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('referencia', sa.String(length=50), nullable=True),
        sa.Column('estado', sa.Boolean(), nullable=False),
        sa.Column('id_miembro', sa.Integer(), nullable=False),
        sa.Column('id_metodo_pago', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_miembro'], ['miembros.id_miembro'], ),
        sa.ForeignKeyConstraint(['id_metodo_pago'], ['metodos_pago.id_metodo_pago'], ),
        sa.PrimaryKeyConstraint('id_pago')
    )

    # Crear tabla comprobantes_pago
    op.create_table('comprobantes_pago',
        sa.Column('id_comprobante', sa.Integer(), nullable=False),
        sa.Column('contenido', sa.LargeBinary(), nullable=False),
        sa.Column('fecha_emision', sa.DateTime(), nullable=False),
        sa.Column('id_pago', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_pago'], ['pagos.id_pago'], ),
        sa.PrimaryKeyConstraint('id_comprobante'),
        sa.UniqueConstraint('id_pago')
    )

    # Crear tabla cuota_mensual
    op.create_table('cuota_mensual',
        sa.Column('id_cuota', sa.Integer(), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id_cuota')
    )

    # Crear tabla miembro_rutina
    op.create_table('miembro_rutina',
        sa.Column('id_miembro', sa.Integer(), nullable=False),
        sa.Column('id_rutina', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_miembro'], ['miembros.id_miembro'], ),
        sa.ForeignKeyConstraint(['id_rutina'], ['rutinas.id_rutina'], ),
        sa.PrimaryKeyConstraint('id_miembro', 'id_rutina')
    )


def downgrade() -> None:
    op.drop_table('miembro_rutina')
    op.drop_table('cuota_mensual')
    op.drop_table('comprobantes_pago')
    op.drop_table('pagos')
    op.drop_table('metodos_pago')
    op.drop_table('miembros')
    op.drop_table('rutinas') 