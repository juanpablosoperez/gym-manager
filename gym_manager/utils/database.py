from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import os
from contextlib import contextmanager
from sqlalchemy.exc import DBAPIError, PendingRollbackError
from pathlib import Path

# Configuración de la base de datos MySQL
from gym_manager.config import DATABASE_URL

# Crear el engine con pool de conexiones y reconexión automática
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Número de conexiones en el pool
    max_overflow=10,  # Máximo número de conexiones adicionales
    pool_timeout=30,  # Tiempo máximo de espera para una conexión
    pool_recycle=3600,  # Reciclar conexiones cada hora
    pool_pre_ping=True,  # Verificar conexión antes de usar
    poolclass=QueuePool,  # Usar QueuePool para mejor manejo de conexiones
)

# Crear la sesión global
Session = sessionmaker(bind=engine)
ScopedSession = scoped_session(Session)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    print("Iniciando nueva sesión de base de datos...")  # Debug log
    session = ScopedSession()
    try:
        print("Sesión creada exitosamente")  # Debug log
        yield session
        print("Haciendo commit de la transacción...")  # Debug log
        session.commit()
        print("Commit exitoso")  # Debug log
    except Exception as e:
        print(f"Error en la transacción, haciendo rollback: {str(e)}")  # Debug log
        session.rollback()
        raise
    finally:
        print("Cerrando sesión...")  # Debug log
        session.close()
        print("Sesión cerrada")  # Debug log

def get_db_session():
    """
    Obtiene una nueva sesión de base de datos
    """
    return ScopedSession()

def cleanup_db_session():
    """
    Limpia la sesión global al cerrar la aplicación
    """
    ScopedSession.remove() 