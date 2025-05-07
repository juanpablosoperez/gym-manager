from sqlalchemy import Column, Integer, Float, DateTime
from gym_manager.services.database import Base

class CuotaMensual(Base):
    __tablename__ = 'cuota_mensual'

    id_cuota = Column(Integer, primary_key=True)
    monto = Column(Float, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo

    def __repr__(self):
        return f"<CuotaMensual(monto={self.monto}, fecha_actualizacion={self.fecha_actualizacion})>" 