from sqlalchemy import Column, Integer, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from gym_manager.models import Base

class ComprobantePago(Base):
    __tablename__ = "comprobantes_pago"

    id_comprobante = Column(Integer, primary_key=True, autoincrement=True)
    contenido = Column(LargeBinary, nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    id_pago = Column(Integer, ForeignKey('pagos.id_pago'), nullable=False, unique=True)

    # Relaciones
    pago = relationship("Pago", back_populates="comprobante")

    def __repr__(self):
        return f"<ComprobantePago(id_comprobante={self.id_comprobante}, id_pago={self.id_pago})>" 