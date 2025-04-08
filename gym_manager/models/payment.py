from sqlalchemy import Column, Integer, DateTime, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from gym_manager.models import Base

class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    fecha_pago = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    referencia = Column(String(50), nullable=True)
    estado = Column(Boolean, nullable=False, default=True)
    id_miembro = Column(Integer, ForeignKey('miembros.id_miembro'), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey('metodos_pago.id_metodo_pago'), nullable=False)

    # Relaciones
    miembro = relationship("Miembro", back_populates="pagos")
    metodo_pago = relationship("MetodoPago", back_populates="pagos")
    comprobante = relationship("ComprobantePago", back_populates="pago", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pago(id_pago={self.id_pago}, monto={self.monto}, id_miembro={self.id_miembro})>"

