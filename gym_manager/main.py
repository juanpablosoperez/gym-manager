# Standard library imports
import os
import sys
import logging
import traceback

# Third-party imports
import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    # Compatibilidad: algunas versiones exponen Colors (CamelCase) en lugar de colors
    ft.colors = ft.Colors
if not hasattr(ft, "icons") and hasattr(ft, "Icons"):
    ft.icons = ft.Icons
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Local imports
from gym_manager.views.login_view import LoginView
from gym_manager.utils.navigation import init_db, navigate_to_login, set_db_session
from gym_manager.controllers.auth_controller import AuthController
from gym_manager.models import Base
from gym_manager.config import DATABASE_URL

# Import mínimo para PyInstaller - solo MySQL driver
try:
    import pymysql
except ImportError:
    pass

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    try:
        # Configurar la página
        page.title = "Gym Manager"
        page.window_icon = "assets/app.ico"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.spacing = 0
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.window_maximizable = True
        page.window_minimizable = True
        # La ventana no se maximiza al inicio, solo después del login
        page.window_maximized = False  # Asegurar que no esté maximizada al inicio
        
        logger.info(f"Usando base de datos: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Error al configurar la página: {e}")
        return
    
    # Inicializar la base de datos
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600
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
    try:
        auth_controller = AuthController(db_session)
        login_view = LoginView(page, auth_controller)
        logger.info("Vista de login inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la vista de login: {e}")
        logger.error(traceback.format_exc())
        # Mostrar una pantalla de error básica
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Error al inicializar la aplicación", size=20, color=ft.colors.RED),
                    ft.Text(f"Detalle: {str(e)}", size=12),
                    ft.ElevatedButton("Cerrar", on_click=lambda _: page.window_destroy())
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        )
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
