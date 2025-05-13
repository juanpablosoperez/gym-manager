from datetime import datetime
from gym_manager.models.payment import Pago
from gym_manager.models.member import Miembro
from gym_manager.models.payment_method import MetodoPago

class PaymentController:
    def __init__(self, db_session=None):
        self.db_session = db_session

    def get_payments(self, filters=None):
        """
        Obtiene la lista de pagos con filtros opcionales
        """
        query = self.db_session.query(Pago)
        
        if filters:
            if filters.get('member_name'):
                query = query.join(Miembro).filter(
                    Miembro.nombre.ilike(f"%{filters['member_name']}%")
                )
            if filters.get('date_from'):
                query = query.filter(Pago.fecha_pago >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(Pago.fecha_pago <= filters['date_to'])
            if filters.get('payment_method'):
                query = query.join(MetodoPago).filter(
                    MetodoPago.descripcion == filters['payment_method']
                )
        
        return query.all()

    def create_payment(self, payment_data):
        """
        Crea un nuevo pago
        """
        try:
            new_payment = Pago(
                fecha_pago=payment_data['fecha_pago'],
                monto=payment_data['monto'],
                referencia=payment_data.get('referencia'),
                estado=True,
                id_miembro=payment_data['id_miembro'],
                id_metodo_pago=payment_data['id_metodo_pago']
            )
            self.db_session.add(new_payment)
            self.db_session.commit()
            return True, "Pago registrado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def update_payment(self, payment_id, payment_data):
        """
        Actualiza un pago existente
        """
        try:
            payment = self.db_session.query(Pago).filter_by(id_pago=payment_id).first()
            if not payment:
                return False, "Pago no encontrado"
            
            for key, value in payment_data.items():
                setattr(payment, key, value)
            
            self.db_session.commit()
            return True, "Pago actualizado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def delete_payment(self, payment_id):
        """
        Elimina un pago
        """
        try:
            payment = self.db_session.query(Pago).filter_by(id_pago=payment_id).first()
            if not payment:
                return False, "Pago no encontrado"
            
            self.db_session.delete(payment)
            self.db_session.commit()
            return True, "Pago eliminado exitosamente"
        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def get_payment_summary(self):
        """
        Obtiene el resumen de pagos
        """
        try:
            total_payments = self.db_session.query(Pago).count()
            pending_payments = self.db_session.query(Pago).filter_by(estado=False).count()
            
            # Obtener el total recaudado en el mes actual
            current_month = datetime.now().month
            current_year = datetime.now().year
            monthly_total = self.db_session.query(Pago).filter(
                extract('month', Pago.fecha_pago) == current_month,
                extract('year', Pago.fecha_pago) == current_year
            ).with_entities(func.sum(Pago.monto)).scalar() or 0
            
            return {
                'total_payments': total_payments,
                'pending_payments': pending_payments,
                'monthly_total': monthly_total
            }
        except Exception as e:
            return {
                'total_payments': 0,
                'pending_payments': 0,
                'monthly_total': 0
            }
