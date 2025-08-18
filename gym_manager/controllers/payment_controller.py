from datetime import datetime
from gym_manager.models.payment import Pago
from gym_manager.models.member import Miembro
from gym_manager.models.payment_method import MetodoPago
from gym_manager.models.payment_receipt import ComprobantePago
from gym_manager.utils.database import session_scope
from sqlalchemy.exc import DBAPIError, PendingRollbackError
from sqlalchemy import func, extract
from sqlalchemy.orm import joinedload

class PaymentController:
    def __init__(self, db_session=None):
        self.db_session = db_session

    def get_payments(self, filters=None):
        """
        Obtiene la lista de pagos con filtros opcionales
        """
        try:
            # Cargar eagerly las relaciones necesarias para evitar DetachedInstanceError
            query = self.db_session.query(Pago).options(
                joinedload(Pago.miembro),
                joinedload(Pago.metodo_pago)
            )
            
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
                
                # Ordenamiento
                if filters.get('order_by'):
                    order_column = getattr(Pago, filters['order_by'], None)
                    if order_column is not None:
                        if filters.get('order_direction') == 'desc':
                            query = query.order_by(order_column.desc())
                        else:
                            query = query.order_by(order_column.asc())
                else:
                    # Ordenamiento por defecto: fecha de pago descendente (más reciente primero)
                    query = query.order_by(Pago.fecha_pago.desc())
                
                # Límite de resultados
                if filters.get('limit'):
                    query = query.limit(filters['limit'])
            else:
                # Si no hay filtros, aplicar ordenamiento por defecto
                query = query.order_by(Pago.fecha_pago.desc())
            
            return query.all()
        except (DBAPIError, PendingRollbackError):
            # Si hay un error de conexión, hacer rollback y reintentar
            self.db_session.rollback()
            return self.get_payments(filters)
        except Exception as e:
            self.db_session.rollback()
            raise

    def create_payment(self, payment_data):
        """
        Crea un nuevo pago
        """
        try:
            # Crear una nueva sesión para esta operación
            with session_scope() as session:
                new_payment = Pago(
                    fecha_pago=payment_data['fecha_pago'],
                    monto=payment_data['monto'],
                    referencia=payment_data.get('referencia'),
                    estado=True,
                    id_miembro=payment_data['id_miembro'],
                    id_metodo_pago=payment_data['id_metodo_pago']
                )
                session.add(new_payment)
                session.flush()  # Esto asegura que se genere el ID
                return True, {"message": "Pago registrado exitosamente", "id_pago": new_payment.id_pago}
        except Exception as e:
            return False, f"Error al crear el pago: {str(e)}"

    def update_payment(self, payment_id, payment_data):
        """
        Actualiza un pago existente
        """
        try:
            with session_scope() as session:
                payment = session.query(Pago).filter_by(id_pago=payment_id).first()
                if not payment:
                    return False, "Pago no encontrado"
                
                for key, value in payment_data.items():
                    setattr(payment, key, value)
                
                return True, "Pago actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar el pago: {str(e)}"

    def delete_payment(self, payment_id):
        """
        Elimina un pago
        """
        try:
            with session_scope() as session:
                payment = session.query(Pago).filter_by(id_pago=payment_id).first()
                if not payment:
                    return False, "Pago no encontrado"
                
                session.delete(payment)
                return True, "Pago eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar el pago: {str(e)}"

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
        except (DBAPIError, PendingRollbackError):
            self.db_session.rollback()
            return {
                'total_payments': 0,
                'pending_payments': 0,
                'monthly_total': 0
            }
        except Exception:
            return {
                'total_payments': 0,
                'pending_payments': 0,
                'monthly_total': 0
            }

    def get_current_month_payments_sum(self):
        """
        Obtiene la suma total de los pagos del mes actual
        """
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            total = self.db_session.query(func.sum(Pago.monto)).filter(
                extract('month', Pago.fecha_pago) == current_month,
                extract('year', Pago.fecha_pago) == current_year,
                Pago.estado == True  # Solo pagos activos
            ).scalar() or 0
            
            return total
        except Exception:
            return 0

    def get_current_year_payments_sum(self):
        """
        Obtiene la suma total de los pagos del año actual
        """
        try:
            current_year = datetime.now().year
            
            total = self.db_session.query(func.sum(Pago.monto)).filter(
                extract('year', Pago.fecha_pago) == current_year,
                Pago.estado == True  # Solo pagos activos
            ).scalar() or 0
            
            return total
        except Exception:
            return 0

    def save_payment_receipt(self, payment_id: int, pdf_content: bytes):
        """
        Guarda el comprobante de pago en la base de datos
        """
        try:
            with session_scope() as session:
                # Verificar si ya existe un comprobante para este pago
                existing_receipt = session.query(ComprobantePago).filter_by(id_pago=payment_id).first()
                
                if existing_receipt:
                    # Actualizar el comprobante existente
                    existing_receipt.contenido = pdf_content
                    existing_receipt.fecha_emision = datetime.now()
                else:
                    # Crear nuevo comprobante
                    new_receipt = ComprobantePago(
                        contenido=pdf_content,
                        fecha_emision=datetime.now(),
                        id_pago=payment_id
                    )
                    session.add(new_receipt)
                
                return True, "Comprobante guardado exitosamente"
        except Exception as e:
            return False, f"Error al guardar el comprobante: {str(e)}"
