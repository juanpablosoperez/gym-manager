from gym_manager.models.payment_method import MetodoPago
from sqlalchemy.orm import Session

class PaymentMethodController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_payment_methods(self, filters=None):
        """
        Obtiene la lista de métodos de pago con filtros opcionales
        """
        query = self.db_session.query(MetodoPago)
        
        if filters:
            if filters.get('search'):
                search = f"%{filters['search']}%"
                query = query.filter(MetodoPago.descripcion.ilike(search))
            if filters.get('status') is not None:
                query = query.filter(MetodoPago.estado == filters['status'])
        
        return query.all()

    def create_payment_method(self, payment_method_data):
        """
        Crea un nuevo método de pago
        """
        try:
            # Verificar si ya existe un método con la misma descripción
            existing_method = self.db_session.query(MetodoPago).filter_by(
                descripcion=payment_method_data['descripcion']
            ).first()
            
            if existing_method:
                return False, "Ya existe un método de pago con esa descripción"

            new_method = MetodoPago(
                descripcion=payment_method_data['descripcion'],
                estado=payment_method_data.get('estado', True)
            )
            
            self.db_session.add(new_method)
            self.db_session.commit()
            return True, "Método de pago registrado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, f"Error al crear el método de pago: {str(e)}"

    def update_payment_method(self, method_id, payment_method_data):
        """
        Actualiza un método de pago existente
        """
        try:
            method = self.db_session.query(MetodoPago).filter_by(id_metodo_pago=method_id).first()
            if not method:
                return False, "Método de pago no encontrado"

            # Verificar si el nuevo nombre ya existe en otro método
            if 'descripcion' in payment_method_data:
                existing_method = self.db_session.query(MetodoPago).filter(
                    MetodoPago.descripcion == payment_method_data['descripcion'],
                    MetodoPago.id_metodo_pago != method_id
                ).first()
                if existing_method:
                    return False, "Ya existe un método de pago con esa descripción"

            for key, value in payment_method_data.items():
                setattr(method, key, value)

            self.db_session.commit()
            return True, "Método de pago actualizado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, f"Error al actualizar el método de pago: {str(e)}"

    def delete_payment_method(self, method_id):
        """
        Elimina un método de pago
        """
        try:
            method = self.db_session.query(MetodoPago).filter_by(id_metodo_pago=method_id).first()
            if not method:
                return False, "Método de pago no encontrado"

            # Verificar si el método está en uso
            if method.pagos:
                return False, "No se puede eliminar el método de pago porque está siendo utilizado en pagos existentes"

            self.db_session.delete(method)
            self.db_session.commit()
            return True, "Método de pago eliminado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, f"Error al eliminar el método de pago: {str(e)}" 