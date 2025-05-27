from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from gym_manager.models.base import Base

class Rutina(Base):
    __tablename__ = 'rutinas'

    id_rutina = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    documento_rutina = Column(LargeBinary)
    nivel_dificultad = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime)
    fecha_horario = Column(DateTime)

    # Relación unidireccional desde Miembro
    miembros = relationship("Miembro", backref="rutina_asignada")

    def __repr__(self):
        return f"<Rutina(id={self.id_rutina}, nombre='{self.nombre}', nivel_dificultad='{self.nivel_dificultad}')>" 