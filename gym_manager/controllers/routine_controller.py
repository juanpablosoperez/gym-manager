from sqlalchemy.exc import SQLAlchemyError
from gym_manager.models.routine import Rutina
from gym_manager.utils.database import get_db_session
import os
import datetime

class RoutineController:
    def __init__(self):
        pass  # Ya no se guarda una sesión

    def assign_routine(self, member_id, file_path, nombre, descripcion, nivel_dificultad, fecha_horario=None):
        """
        Asigna una rutina a un miembro
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return False, "El archivo no existe"

            # Obtener el nombre y tipo del archivo
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1].lower().replace('.', '')

            # Verificar que el tipo de archivo es válido
            if file_type not in ['pdf', 'xlsx', 'xls']:
                return False, "Tipo de archivo no válido. Solo se permiten PDF y Excel"

            # Leer el archivo
            with open(file_path, 'rb') as file:
                file_content = file.read()

            # Crear la rutina
            session = get_db_session()
            try:
                rutina = Rutina(
                    id_miembro=member_id,
                    nombre=nombre,
                    descripcion=descripcion,
                    documento_rutina=file_content,
                    nivel_dificultad=nivel_dificultad,
                    fecha_horario=fecha_horario
                )
                session.add(rutina)
                session.commit()
                return True, "Rutina asignada exitosamente"
            except Exception as e:
                session.rollback()
                return False, f"Error al asignar la rutina: {str(e)}"
            finally:
                session.close()
        except SQLAlchemyError as e:
            return False, f"Error al asignar la rutina: {str(e)}"

    def get_member_routines(self, member_id):
        """
        Obtiene las rutinas de un miembro
        """
        session = get_db_session()
        try:
            return session.query(Rutina).filter_by(id_miembro=member_id).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener rutinas: {str(e)}")
            return []
        finally:
            session.close()

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
            print(f"Error al contar miembros asignados a rutina {routine_id}: {str(e)}")
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
<<<<<<< HEAD
            valid_fields = ['nombre', 'descripcion', 'documento_rutina', 'nivel_dificultad', 'fecha_creacion', 'fecha_horario']
=======
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
            
>>>>>>> develop
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