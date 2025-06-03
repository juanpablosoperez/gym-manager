import flet as ft
from gym_manager.utils.database import get_db_session, cleanup_db_session
import os
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import Session

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable global para la sesión de la base de datos
db_session: Session = None

def set_db_session(session: Session):
    """Establece la sesión de la base de datos global"""
    global db_session
    db_session = session
    logger.info("Sesión de base de datos establecida globalmente")

def init_db():
    """Inicializa la base de datos"""
    try:
        from gym_manager.models import Base
        from gym_manager.utils.database import engine
        Base.metadata.create_all(engine)
        logger.info("Base de datos inicializada exitosamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise

def navigate_to_login(page: ft.Page):
    # Limpiar la página actual
    page.clean()
    
    # Configurar página para login
    page.title = "Login - Gym Manager"
    page.window_width = 400
    page.window_height = 500
    page.window_resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.WHITE
    page.update()
    
    # Importar aquí para evitar circular import
    from gym_manager.controllers.auth_controller import AuthController
    from gym_manager.views.login_view import LoginView
    
    # Crear y mostrar vista de login
    auth_controller = AuthController(get_db_session())
    LoginView(page, auth_controller)

def navigate_to_home(page: ft.Page, user_rol: str, user_name: str):
    # Limpiar la página actual
    page.clean()
    
    # Configurar página para home
    page.title = "Gym Manager - Home"
    page.padding = 0
    page.bgcolor = ft.colors.GREY_50
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True
    page.update()
    
    try:
        # Importar aquí para evitar circular import
        from gym_manager.views.home_view import HomeView
        # Crear y mostrar vista de home
        HomeView(page, user_rol, user_name)
    except Exception as e:
        logger.error(f"Error al cargar la vista principal: {str(e)}")
        # Mostrar mensaje de error en la página
        page.add(ft.Text("Error al cargar la vista principal", color=ft.colors.RED))
        page.update()

def cleanup():
    """Cleanup resources when the application closes."""
    cleanup_db_session() 