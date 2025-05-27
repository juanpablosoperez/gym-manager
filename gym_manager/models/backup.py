from sqlalchemy import Column, Integer, String, Float, DateTime, Text, CheckConstraint
from gym_manager.models import Base
from datetime import datetime

class Backup(Base):
    """
    Modelo que representa un backup de la base de datos.
    
    Attributes:
        id (int): Identificador único del backup
        name (str): Nombre del archivo de backup
        file_path (str): Ruta completa al archivo de backup
        size_mb (float): Tamaño del archivo en megabytes
        status (str): Estado del backup (completed, failed, in_progress)
        created_at (datetime): Fecha y hora de creación del backup
        error_message (str): Mensaje de error si el backup falló
        description (str): Descripción opcional del backup
        created_by (str): Usuario que creó el backup
    """
    __tablename__ = 'backups'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    file_path = Column(String(255), nullable=False)
    size_mb = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # completed, failed, in_progress
    created_at = Column(DateTime, default=datetime.now)
    error_message = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)

    # Agregar restricción para el estado
    __table_args__ = (
        CheckConstraint(
            status.in_(['completed', 'failed', 'in_progress']),
            name='check_backup_status'
        ),
    )

    def __repr__(self):
        return f"<Backup(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def is_completed(self) -> bool:
        """Verifica si el backup se completó exitosamente"""
        return self.status == 'completed'

    @property
    def is_failed(self) -> bool:
        """Verifica si el backup falló"""
        return self.status == 'failed'

    @property
    def is_in_progress(self) -> bool:
        """Verifica si el backup está en progreso"""
        return self.status == 'in_progress' 