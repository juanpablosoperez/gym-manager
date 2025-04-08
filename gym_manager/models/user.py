from sqlalchemy import Column, Integer, String, Boolean
from gym_manager.models import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    rol = Column(String(20), nullable=False)
    contraseña = Column(String(100), nullable=False)
    estado = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Usuario(id_usuario={self.id_usuario}, nombre={self.nombre}, apellido={self.apellido}, rol={self.rol})>"
