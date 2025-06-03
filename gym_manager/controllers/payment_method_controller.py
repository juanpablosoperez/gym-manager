from gym_manager.models.payment_method import MetodoPago
from gym_manager.models.payment import Pago
from sqlalchemy.orm import Session, joinedload
from gym_manager.utils.database import session_scope
from sqlalchemy.exc import DBAPIError, PendingRollbackError

class PaymentMethodController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_payment_methods(self, filters=None):
        """
        Obtiene la lista de métodos de pago con filtros opcionales
        """
        try:
            with session_scope() as session:
                # Cargar explícitamente la relación pagos y sus relaciones
                query = session.query(MetodoPago).options(
                    joinedload(MetodoPago.pagos).joinedload(Pago.miembro)
                )
                
                if filters:
                    if filters.get('search'):
                        search = f"%{filters['search']}%"
                        query = query.filter(MetodoPago.descripcion.ilike(search))
                    if filters.get('status') is not None:
                        query = query.filter(MetodoPago.estado == filters['status'])
                
                # Obtener los métodos y asegurarse de que estén adjuntos a la sesión
                methods = query.all()
                
                # Convertir los objetos a diccionarios para evitar problemas de sesión
                result = []
                for method in methods:
                    result.append({
                        'id_metodo_pago': method.id_metodo_pago,
                        'descripcion': method.descripcion,
                        'estado': method.estado,
                        'pagos': [{
                            'id_pago': pago.id_pago,
                            'monto': pago.monto,
                            'fecha_pago': pago.fecha_pago,
                            'miembro': {
                                'nombre': pago.miembro.nombre,
                                'apellido': pago.miembro.apellido
                            } if pago.miembro else None
                        } for pago in method.pagos]
                    })
                
                return result
        except (DBAPIError, PendingRollbackError) as e:
            print(f"Error de base de datos: {str(e)}")
            # Intentar reconectar
            try:
                self.db_session.rollback()
            except:
                pass
            raise Exception("Error al conectar con la base de datos. Por favor, intente nuevamente.")

    def create_payment_method(self, payment_method_data):
        """
        Crea un nuevo método de pago
        """
        try:
            with session_scope() as session:
                # Verificar si ya existe un método con la misma descripción
                existing_method = session.query(MetodoPago).filter_by(
                    descripcion=payment_method_data['descripcion']
                ).first()
                
                if existing_method:
                    return False, "Ya existe un método de pago con esa descripción"

                new_method = MetodoPago(
                    descripcion=payment_method_data['descripcion'],
                    estado=payment_method_data.get('estado', True)
                )
                
                session.add(new_method)
                return True, "Método de pago registrado exitosamente"
        except Exception as e:
            return False, f"Error al crear el método de pago: {str(e)}"

    def update_payment_method(self, method_id, payment_method_data):
        """
        Actualiza un método de pago existente
        """
        try:
            with session_scope() as session:
                method = session.query(MetodoPago).filter_by(id_metodo_pago=method_id).first()
                if not method:
                    return False, "Método de pago no encontrado"

                # Verificar si el nuevo nombre ya existe en otro método
                if 'descripcion' in payment_method_data:
                    existing_method = session.query(MetodoPago).filter(
                        MetodoPago.descripcion == payment_method_data['descripcion'],
                        MetodoPago.id_metodo_pago != method_id
                    ).first()
                    if existing_method:
                        return False, "Ya existe un método de pago con esa descripción"

                for key, value in payment_method_data.items():
                    setattr(method, key, value)

                return True, "Método de pago actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar el método de pago: {str(e)}"

    def delete_payment_method(self, method_id):
        """
        Elimina un método de pago
        """
        try:
            with session_scope() as session:
                method = session.query(MetodoPago).filter_by(id_metodo_pago=method_id).first()
                if not method:
                    return False, "Método de pago no encontrado"

                # Verificar si el método está en uso
                if method.pagos:
                    return False, "No se puede eliminar el método de pago porque está siendo utilizado en pagos existentes"

                session.delete(method)
                return True, "Método de pago eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar el método de pago: {str(e)}" 