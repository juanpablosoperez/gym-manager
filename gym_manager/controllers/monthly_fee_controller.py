from datetime import datetime
from gym_manager.models.monthly_fee import CuotaMensual
from sqlalchemy.orm import Session
from gym_manager.utils.database import session_scope
from sqlalchemy.exc import DBAPIError, PendingRollbackError

class MonthlyFeeController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_current_fee(self):
        """
        Obtiene la cuota mensual actual
        """
        try:
            return self.db_session.query(CuotaMensual).filter_by(activo=1).first()
        except (DBAPIError, PendingRollbackError):
            self.db_session.rollback()
            return self.get_current_fee()

    def update_fee(self, new_amount: float):
        """
        Actualiza la cuota mensual
        """
        try:
            with session_scope() as session:
                # Desactivar la cuota actual
                current_fee = session.query(CuotaMensual).filter_by(activo=1).first()
                if current_fee:
                    current_fee.activo = 0

                # Crear nueva cuota
                new_fee = CuotaMensual(
                    monto=new_amount,
                    fecha_actualizacion=datetime.now(),
                    activo=1
                )
                session.add(new_fee)
                return True, "Cuota mensual actualizada correctamente"
        except Exception as e:
            return False, f"Error al actualizar la cuota mensual: {str(e)}"

    def initialize_fee(self, initial_amount: float):
        """
        Inicializa la cuota mensual si no existe
        """
        try:
            with session_scope() as session:
                if not session.query(CuotaMensual).filter_by(activo=1).first():
                    new_fee = CuotaMensual(
                        monto=initial_amount,
                        fecha_actualizacion=datetime.now(),
                        activo=1
                    )
                    session.add(new_fee)
                    return True, "Cuota mensual inicializada correctamente"
                return False, "Ya existe una cuota mensual activa"
        except Exception as e:
            return False, f"Error al inicializar la cuota mensual: {str(e)}" 