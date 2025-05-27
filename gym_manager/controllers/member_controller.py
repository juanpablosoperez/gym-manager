from gym_manager.models.member import Miembro
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import logging

class MemberController:
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    def get_members(self):
        """
        Obtiene la lista de todos los miembros
        """
        try:
            return self.db_session.query(Miembro).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener miembros: {str(e)}")
            self.db_session.rollback()
            raise

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
        Elimina un miembro (cambia su estado a inactivo)
        """
        try:
            member = self.db_session.query(Miembro).filter_by(id_miembro=member_id).first()
            if not member:
                return False, "Miembro no encontrado"

            member.estado = False
            self.db_session.commit()
            return True, "Miembro eliminado exitosamente"
        except SQLAlchemyError as e:
            self.logger.error(f"Error al eliminar miembro: {str(e)}")
            self.db_session.rollback()
            return False, f"Error al eliminar el miembro: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error inesperado al eliminar miembro: {str(e)}")
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