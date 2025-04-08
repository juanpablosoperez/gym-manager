from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from gym_manager.models import Base

class MetodoPago(Base):
    __tablename__ = "metodos_pago"

    id_metodo_pago = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(50), nullable=False)
    estado = Column(Boolean, nullable=False, default=True)

    # Relaciones
    pagos = relationship("Pago", back_populates="metodo_pago")

    def __repr__(self):
        return f"<MetodoPago(id_metodo_pago={self.id_metodo_pago}, descripcion={self.descripcion})>" 