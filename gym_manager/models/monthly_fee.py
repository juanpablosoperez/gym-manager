from sqlalchemy import Column, Integer, Float, DateTime, Boolean
from gym_manager.models import Base

class CuotaMensual(Base):
    __tablename__ = 'cuota_mensual'

    id_cuota = Column(Integer, primary_key=True, autoincrement=True)
    monto = Column(Float, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<CuotaMensual(monto={self.monto}, fecha_actualizacion={self.fecha_actualizacion})>" 