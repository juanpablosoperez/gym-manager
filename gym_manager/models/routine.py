from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from gym_manager.models import Base

class Rutina(Base):
    __tablename__ = "rutinas"

    id_rutina = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    documento_rutina = Column(LargeBinary, nullable=True)
    nivel_dificultad = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_horario = Column(DateTime, nullable=False)
    id_miembro = Column(Integer, ForeignKey('miembros.id_miembro'), nullable=False)

    # Relaciones
    miembro = relationship("Miembro", back_populates="rutinas")

    def __repr__(self):
        return f"<Rutina(id_rutina={self.id_rutina}, nombre={self.nombre}, id_miembro={self.id_miembro})>" 