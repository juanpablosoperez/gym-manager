from gym_manager.models.user import Usuario
from gym_manager.utils.database import get_db_session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class UserController:
    def __init__(self):
        self.db_session = get_db_session()

    def get_users(self):
        """Obtiene todos los usuarios del sistema ordenados por ID descendente (más recientes primero)."""
        try:
            return self.db_session.query(Usuario).order_by(Usuario.id_usuario.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener usuarios: {str(e)}")
            return []

    def get_user_by_id(self, user_id):
        """Obtiene un usuario por su ID."""
        try:
            return self.db_session.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener usuario por ID: {str(e)}")
            return None

    def get_user_by_name(self, nombre, apellido):
        """Obtiene un usuario por su nombre y apellido."""
        try:
            return self.db_session.query(Usuario).filter(
                Usuario.nombre == nombre,
                Usuario.apellido == apellido
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener usuario por nombre: {str(e)}")
            return None

    def create_user(self, nombre, apellido, rol, contraseña):
        """Crea un nuevo usuario."""
        try:
            if self.get_user_by_name(nombre, apellido):
                return False, "El usuario ya existe"
            
            new_user = Usuario(nombre=nombre, apellido=apellido, rol=rol, contraseña=contraseña)
            self.db_session.add(new_user)
            self.db_session.commit()
            return True, "Usuario creado exitosamente"
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Error al crear usuario: {str(e)}")
            return False, "Error al crear el usuario"

    def update_user(self, user_id, **kwargs):
        """Actualiza los datos de un usuario."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Usuario no encontrado"
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    if key == 'contraseña':
                        # Solo actualizar la contraseña si se proporciona una nueva
                        if value is not None and value.strip() != "":
                            user.set_password(value)
                    else:
                        setattr(user, key, value)
            
            self.db_session.commit()
            return True, "Usuario actualizado exitosamente"
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Error al actualizar usuario: {str(e)}")
            return False, "Error al actualizar el usuario"

    def delete_user(self, user_id):
        """Elimina un usuario."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Usuario no encontrado"
            
            self.db_session.delete(user)
            self.db_session.commit()
            return True, "Usuario eliminado exitosamente"
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Error al eliminar usuario: {str(e)}")
            return False, "Error al eliminar el usuario"

    def __del__(self):
        """Cierra la sesión de la base de datos al destruir el controlador."""
        if hasattr(self, 'db_session'):
            self.db_session.close()
