from datetime import datetime
from gym_manager.models.payment_receipt import ComprobantePago
from gym_manager.utils.database import session_scope
from sqlalchemy.exc import DBAPIError, PendingRollbackError, SQLAlchemyError
import logging

class PaymentReceiptController:
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    def get_receipts(self, filters=None):
        """
        Obtiene la lista de comprobantes con filtros opcionales
        """
        try:
            with session_scope() as session:
                query = session.query(ComprobantePago).join(ComprobantePago.pago)
                
                if filters:
                    if filters.get('fecha_desde'):
                        query = query.filter(ComprobantePago.fecha_emision >= filters['fecha_desde'])
                    if filters.get('fecha_hasta'):
                        query = query.filter(ComprobantePago.fecha_emision <= filters['fecha_hasta'])
                
                # Ordenar por fecha de emisión descendente
                query = query.order_by(ComprobantePago.fecha_emision.desc())
                
                receipts = query.all()
                return [
                    {
                        'id_comprobante': r.id_comprobante,
                        'fecha_emision': r.fecha_emision,
                        'id_pago': r.id_pago,
                        'miembro': f"{r.pago.miembro.nombre} {r.pago.miembro.apellido}",
                        'monto': r.pago.monto,
                        'metodo_pago': r.pago.metodo_pago.descripcion
                    }
                    for r in receipts
                ]
        except Exception as e:
            self.logger.error(f"Error al obtener comprobantes: {str(e)}")
            return []

    def get_receipt_content(self, receipt_id):
        """
        Obtiene el contenido del comprobante
        """
        try:
            with session_scope() as session:
                receipt = session.query(ComprobantePago).filter_by(id_comprobante=receipt_id).first()
                if receipt:
                    return receipt.contenido
                return None
        except Exception as e:
            self.logger.error(f"Error al obtener contenido del comprobante: {str(e)}")
            return None 