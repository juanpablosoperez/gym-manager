from datetime import datetime
from gym_manager.models.monthly_fee import CuotaMensual
from sqlalchemy.orm import Session

class MonthlyFeeController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_current_fee(self):
        """
        Obtiene la cuota mensual actual
        """
        return self.db_session.query(CuotaMensual).filter_by(activo=1).first()

    def update_fee(self, new_amount: float):
        """
        Actualiza la cuota mensual
        """
        try:
            # Desactivar la cuota actual
            current_fee = self.get_current_fee()
            if current_fee:
                current_fee.activo = 0

            # Crear nueva cuota
            new_fee = CuotaMensual(
                monto=new_amount,
                fecha_actualizacion=datetime.now(),
                activo=1
            )
            self.db_session.add(new_fee)
            self.db_session.commit()
            return True, "Cuota mensual actualizada correctamente"
        except Exception as e:
            self.db_session.rollback()
            return False, f"Error al actualizar la cuota mensual: {str(e)}"

    def initialize_fee(self, initial_amount: float):
        """
        Inicializa la cuota mensual si no existe
        """
        if not self.get_current_fee():
            new_fee = CuotaMensual(
                monto=initial_amount,
                fecha_actualizacion=datetime.now(),
                activo=1
            )
            self.db_session.add(new_fee)
            self.db_session.commit()
            return True, "Cuota mensual inicializada correctamente"
        return False, "Ya existe una cuota mensual activa" 