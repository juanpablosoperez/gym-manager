from sqlalchemy.exc import SQLAlchemyError
import datetime

from gym_manager.models.routine import Rutina
from gym_manager.utils.database import get_db_session

class RoutineController:
    def __init__(self):
        pass  # Ya no se guarda una sesión

    def get_routines(self, filters=None):
        """
        Obtiene todas las rutinas, opcionalmente filtradas
        """
        session = get_db_session()
        try:
            query = session.query(Rutina)

            if filters:
                if filters.get('search'):
                    search = f"%{filters['search']}%"
                    query = query.filter(Rutina.nombre.ilike(search))

                if filters.get('nivel_dificultad'):
                    query = query.filter(Rutina.nivel_dificultad == filters['nivel_dificultad'])

            return query.all()
        finally:
            session.close()

    def get_routine_by_id(self, routine_id: int):
        """
        Obtiene una rutina por su ID
        """
        session = get_db_session()
        try:
            return session.query(Rutina).filter(Rutina.id_rutina == routine_id).first()
        finally:
            session.close()

    def count_members_assigned_to_routine(self, routine_id: int):
        """
        Cuenta cuántos miembros tienen asignada una rutina específica por su ID.
        """
        session = get_db_session()
        try:
            from gym_manager.models.member import Miembro  # Importar Miembro aquí para evitar dependencia circular si la hay
            count = session.query(Miembro).filter(Miembro.id_rutina == routine_id).count()
            return count
        except Exception as e:
            return 0
        finally:
            session.close()

    def create_routine(self, routine_data: dict):
        """
        Crea una nueva rutina
        """
        session = get_db_session()
        try:
            # Solo tomar los campos válidos
            valid_fields = ['nombre', 'descripcion', 'documento_rutina', 'nivel_dificultad', 'fecha_creacion', 'fecha_horario', 'id_miembro']
            now = datetime.datetime.now()
            # Refuerzo: si faltan los campos, los agrego
            if 'fecha_creacion' not in routine_data or not routine_data['fecha_creacion']:
                routine_data['fecha_creacion'] = now
            if 'fecha_horario' not in routine_data or not routine_data['fecha_horario']:
                routine_data['fecha_horario'] = now
            
            # Validar tamaño del archivo si existe
            if 'documento_rutina' in routine_data and routine_data['documento_rutina']:
                MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB en bytes
                file_size = len(routine_data['documento_rutina'])
                if file_size > MAX_FILE_SIZE:
                    return False, f"El archivo es demasiado grande. Máximo permitido: 1MB. Tu archivo: {file_size / (1024*1024):.1f}MB"
            
            filtered_data = {k: v for k, v in routine_data.items() if k in valid_fields}
            routine = Rutina(**filtered_data)
            session.add(routine)
            session.commit()
            return True, "Rutina creada exitosamente"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def update_routine(self, routine_id: int, routine_data: dict):
        """
        Actualiza una rutina existente
        """
        session = get_db_session()
        try:
            routine = session.query(Rutina).filter(Rutina.id_rutina == routine_id).first()
            if not routine:
                return False, "Rutina no encontrada"

            # Validar tamaño del archivo si se está actualizando
            if 'documento_rutina' in routine_data and routine_data['documento_rutina']:
                MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB en bytes
                file_size = len(routine_data['documento_rutina'])
                if file_size > MAX_FILE_SIZE:
                    return False, f"El archivo es demasiado grande. Máximo permitido: 1MB. Tu archivo: {file_size / (1024*1024):.1f}MB"

            for key, value in routine_data.items():
                setattr(routine, key, value)

            session.commit()
            return True, "Rutina actualizada exitosamente"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def delete_routine(self, routine_id: int):
        """
        Elimina una rutina
        """
        session = get_db_session()
        try:
            routine = session.query(Rutina).filter(Rutina.id_rutina == routine_id).first()
            if not routine:
                return False, "Rutina no encontrada"

            session.delete(routine)
            session.commit()
            return True, "Rutina eliminada exitosamente"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()