from gym_manager.models.member import Miembro
from datetime import datetime

class MemberController:
    def __init__(self, db_session=None):
        self.db_session = db_session

    def get_members(self, filters=None):
        """
        Obtiene la lista de miembros con filtros opcionales
        """
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
        
        return query.all()

    def create_member(self, member_data):
        """
        Crea un nuevo miembro
        """
        print("Iniciando creación de miembro en el controlador...")  # Debug log
        try:
            print("Datos recibidos:", member_data)  # Debug log
            
            # Verificar si ya existe un miembro con el mismo documento
            existing_member = self.db_session.query(Miembro).filter_by(documento=member_data['documento']).first()
            if existing_member:
                print("Ya existe un miembro con ese documento")  # Debug log
                return False, "Ya existe un miembro con ese número de documento"

            new_member = Miembro(
                nombre=member_data['nombre'],
                apellido=member_data['apellido'],
                documento=member_data['documento'],
                fecha_nacimiento=member_data['fecha_nacimiento'],
                genero=member_data['genero'],
                correo_electronico=member_data['correo_electronico'],
                estado=member_data.get('estado', True),
                tipo_membresia=member_data['tipo_membresia'],
                direccion=member_data.get('direccion'),
                telefono=member_data.get('telefono'),
                fecha_registro=datetime.now(),
                informacion_medica=member_data.get('informacion_medica')
            )
            
            print("Objeto Miembro creado:", new_member)  # Debug log
            
            self.db_session.add(new_member)
            print("Miembro agregado a la sesión")  # Debug log
            
            self.db_session.commit()
            print("Cambios guardados en la base de datos")  # Debug log
            
            return True, "Miembro registrado exitosamente"
        except Exception as e:
            print(f"Error al crear miembro: {str(e)}")  # Debug log
            self.db_session.rollback()
            return False, f"Error al crear el miembro: {str(e)}"

    def update_member(self, member_id, member_data):
        """
        Actualiza un miembro existente
        """
        try:
            member = self.db_session.query(Miembro).filter_by(id_miembro=member_id).first()
            if not member:
                return False, "Miembro no encontrado"

            for key, value in member_data.items():
                setattr(member, key, value)

            self.db_session.commit()
            return True, "Miembro actualizado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def delete_member(self, member_id):
        """
        Elimina un miembro
        """
        try:
            member = self.db_session.query(Miembro).filter_by(id_miembro=member_id).first()
            if not member:
                return False, "Miembro no encontrado"

            self.db_session.delete(member)
            self.db_session.commit()
            return True, "Miembro eliminado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, str(e) 