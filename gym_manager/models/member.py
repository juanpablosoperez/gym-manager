from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from gym_manager.models import Base

class Miembro(Base):
    __tablename__ = "miembros"

    id_miembro = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    documento = Column(String(20), nullable=False, unique=True)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String(10), nullable=False)
    correo_electronico = Column(String(100), nullable=False, unique=True)
    estado = Column(Boolean, nullable=False, default=True)
    tipo_membresia = Column(String(20), nullable=False)
    direccion = Column(String(200), nullable=True)
    telefono = Column(String(20), nullable=True)
    fecha_registro = Column(DateTime, nullable=False)
    informacion_medica = Column(Text, nullable=True)

    # Relaciones
    rutinas = relationship("Rutina", back_populates="miembro", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="miembro", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Miembro(id_miembro={self.id_miembro}, nombre={self.nombre}, apellido={self.apellido})>" 