from gym_manager.models.member import Miembro
from gym_manager.models.payment import Pago
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
import logging

class MemberController:
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    def get_members(self, filters=None):
        """
        Obtiene la lista de todos los miembros con filtros opcionales
        """
        try:
            query = self.db_session.query(Miembro)
            
            if filters:
                if filters.get('search'):
                    search = f"%{filters['search']}%"
                    query = query.filter(
                        (Miembro.nombre.ilike(search)) |
                        (Miembro.apellido.ilike(search)) |
                        (Miembro.documento.ilike(search)) |
                        (Miembro.correo_electronico.ilike(search))
                    )
                if filters.get('status') is not None:
                    query = query.filter(Miembro.estado == filters['status'])
                if filters.get('membership_type'):
                    query = query.filter(Miembro.tipo_membresia == filters['membership_type'])
                if filters.get('fecha_registro_desde'):
                    query = query.filter(Miembro.fecha_registro >= filters['fecha_registro_desde'])
                if filters.get('fecha_registro_hasta'):
                    query = query.filter(Miembro.fecha_registro <= filters['fecha_registro_hasta'])
                
                # Ordenamiento
                if filters.get('order_by'):
                    order_column = getattr(Miembro, filters['order_by'], None)
                    if order_column is not None:
                        if filters.get('order_direction') == 'desc':
                            query = query.order_by(order_column.desc())
                        else:
                            query = query.order_by(order_column.asc())
                
                # Límite de resultados
                if filters.get('limit'):
                    query = query.limit(filters['limit'])
            
            return query.all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error de base de datos: {str(e)}")
            self.db_session.rollback()
            raise Exception("Error al conectar con la base de datos. Por favor, intente nuevamente.")

    def get_member(self, member_id):
        """
        Obtiene un miembro por su ID
        """
        try:
            return self.db_session.query(Miembro).filter_by(id_miembro=member_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener miembro {member_id}: {str(e)}")
            self.db_session.rollback()
            raise

    def create_member(self, member_data):
        """
        Crea un nuevo miembro
        """
        try:
            # Validar si el documento ya existe
            existing = self.db_session.query(Miembro).filter_by(documento=member_data['documento']).first()
            if existing:
                return False, "Ya existe un miembro con ese documento. Por favor, ingrese uno diferente."
            new_member = Miembro(
                nombre=member_data['nombre'],
                apellido=member_data['apellido'],
                documento=member_data['documento'],
                fecha_nacimiento=member_data['fecha_nacimiento'],
                genero=member_data['genero'],
                correo_electronico=member_data.get('correo_electronico'),
                estado=True,
                tipo_membresia=member_data.get('tipo_membresia'),
                direccion=member_data.get('direccion'),
                telefono=member_data.get('telefono'),
                fecha_registro=datetime.now(),
                informacion_medica=member_data.get('informacion_medica')
            )
            self.db_session.add(new_member)
            self.db_session.commit()
            return True, "Miembro registrado exitosamente"
        except SQLAlchemyError as e:
            self.logger.error(f"Error al crear miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error al crear el miembro: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error inesperado al crear miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error inesperado: {str(e)}"

    def update_member(self, member_id, member_data):
        """
        Actualiza un miembro existente
        """
        try:
            member = self.db_session.query(Miembro).filter_by(id_miembro=member_id).first()
            if not member:
                return False, "Miembro no encontrado"

            member.nombre = member_data['nombre']
            member.apellido = member_data['apellido']
            member.documento = member_data['documento']
            member.fecha_nacimiento = member_data['fecha_nacimiento']
            member.genero = member_data['genero']
            member.correo_electronico = member_data.get('correo_electronico')
            member.tipo_membresia = member_data.get('tipo_membresia')
            member.direccion = member_data.get('direccion')
            member.telefono = member_data.get('telefono')
            member.informacion_medica = member_data.get('informacion_medica')
            if 'estado' in member_data:
                member.estado = member_data['estado']

            self.db_session.commit()
            return True, "Miembro actualizado exitosamente"
        except SQLAlchemyError as e:
            self.logger.error(f"Error al actualizar miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error al actualizar el miembro: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error inesperado al actualizar miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error inesperado: {str(e)}"

    def delete_member(self, member_id):
        """
        Desactiva un miembro (cambia su estado a inactivo) en vez de eliminarlo físicamente.
        """
        try:
            member = self.db_session.query(Miembro).filter_by(id_miembro=member_id).first()
            if not member:
                return False, "Miembro no encontrado"
            member.estado = False
            self.db_session.commit()
            return True, "Miembro desactivado exitosamente"
        except SQLAlchemyError as e:
            self.logger.error(f"Error al desactivar miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error al desactivar el miembro: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error inesperado al desactivar miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error inesperado: {str(e)}"

    def search_members(self, search_term):
        """
        Busca miembros por nombre, apellido o documento
        """
        try:
            return self.db_session.query(Miembro).filter(
                (Miembro.nombre.ilike(f"%{search_term}%")) |
                (Miembro.apellido.ilike(f"%{search_term}%")) |
                (Miembro.documento.ilike(f"%{search_term}%"))
            ).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error al buscar miembros: {str(e)}")
            self.db_session.rollback()
            raise

    def get_active_members_count(self):
        """
        Obtiene el conteo total de miembros activos
        """
        try:
            count = self.db_session.query(func.count(Miembro.id_miembro)).filter(
                Miembro.estado == True
            ).scalar()
            return count or 0
        except Exception as e:
            self.logger.error(f"Error al contar miembros activos: {str(e)}")
            return 0

    def get_expired_memberships_count(self):
        """
        Obtiene el conteo de membresías vencidas (último pago hace más de 30 días)
        """
        try:
            # Obtener la fecha límite (30 días atrás)
            fecha_limite = datetime.now() - timedelta(days=30)
            
            # Subconsulta para obtener el último pago de cada miembro
            subquery = self.db_session.query(
                Pago.id_miembro,
                func.max(Pago.fecha_pago).label('ultima_fecha_pago')
            ).filter(
                Pago.estado == True  # Solo pagos activos
            ).group_by(Pago.id_miembro).subquery()
            
            # Contar miembros cuyo último pago fue antes de la fecha límite
            count = self.db_session.query(func.count(Miembro.id_miembro)).join(
                subquery,
                Miembro.id_miembro == subquery.c.id_miembro
            ).filter(
                and_(
                    Miembro.estado == True,  # Solo miembros activos
                    subquery.c.ultima_fecha_pago < fecha_limite
                )
            ).scalar()
            
            return count or 0
        except Exception as e:
            self.logger.error(f"Error al contar membresías vencidas: {str(e)}")
            return 0

    def assign_routine_to_member(self, member_id, routine_id):
        """
        Asigna una rutina a un miembro (solo actualiza el campo id_rutina)
        """
        try:
            member = self.db_session.query(Miembro).filter_by(id_miembro=member_id).first()
            if not member:
                return False, "Miembro no encontrado"

            member.id_rutina = routine_id
            self.db_session.commit()
            return True, "Rutina asignada exitosamente"
        except SQLAlchemyError as e:
            self.logger.error(f"Error al asignar rutina al miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error al asignar la rutina: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error inesperado al asignar rutina: {str(e)}")
            self.db_session.rollback()
            return False, f"Error inesperado: {str(e)}"
