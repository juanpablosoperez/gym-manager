# Standard library imports
import os
import sys
import logging
import traceback

# Third-party imports
import flet as ft
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Local imports
from gym_manager.views.login_view import LoginView
from gym_manager.controllers.auth_controller import AuthController
from gym_manager.models import Base
from gym_manager.utils.navigation import set_db_session

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar la página
    page.title = "Gym Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True
    page.window_maximizable = True
    page.window_minimizable = True
    
    # Configuración de la base de datos MySQL
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'gym_manager')
    
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Inicializar la base de datos
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(engine)
        logger.info("Tablas creadas exitosamente")
        
        # Probar la conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
            count = result.scalar()
            logger.info(f"Conexión exitosa. Total de usuarios: {count}")
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        logger.error(traceback.format_exc())
        return
    
    # Crear sesión de base de datos
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    # Establecer la sesión de la base de datos
    set_db_session(db_session)
    
    # Función para limpiar recursos de la base de datos
    def cleanup_db(engine, db_session):
        logger.info("Iniciando limpieza de recursos de base de datos...")
        try:
            if db_session:
                db_session.close()
                logger.info("Sesión de base de datos cerrada")
            if engine:
                engine.dispose()
                logger.info("Pool de conexiones liberado")
            logger.info("Limpieza de recursos de base de datos completada")
        except Exception as e:
            logger.error(f"Error durante la limpieza de la base de datos: {e}")
            logger.error(traceback.format_exc())
    
    # Manejar el cierre de la ventana
    def on_window_close(e):
        logger.info("Ventana cerrada por el usuario")
        cleanup_db(engine, db_session)
        page.window_destroy()
    
    page.on_window_close = on_window_close
    
    # Inicializar la vista de login
    auth_controller = AuthController(db_session)
    LoginView(page, auth_controller)

if __name__ == "__main__":
    ft.app(target=main)

