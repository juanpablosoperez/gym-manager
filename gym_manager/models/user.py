from sqlalchemy import Column, Integer, String, Boolean
from gym_manager.models import Base
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    rol = Column(String(20), nullable=False)
    contraseña = Column(String(100), nullable=False)
    estado = Column(Boolean, nullable=False, default=True)

    def __init__(self, nombre, apellido, rol, contraseña):
        self.nombre = nombre
        self.apellido = apellido
        self.rol = rol
        self.set_password(contraseña)
        self.estado = True

    def set_password(self, contraseña):
        self.contraseña = generate_password_hash(contraseña)

    def check_password(self, contraseña):
        return check_password_hash(self.contraseña, contraseña)

    def __repr__(self):
    
        return f"<Usuario(id_usuario={self.id_usuario}, nombre={self.nombre}, rol={self.rol})>"
