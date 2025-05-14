import flet as ft
from gym_manager.views.login_view import LoginView
from gym_manager.controllers.auth_controller import AuthController
from gym_manager.models import Base
from gym_manager.utils.database import get_db_session, cleanup_db_session
from gym_manager.utils.navigation import set_db_session
import os
from dotenv import load_dotenv

def main():
    def init(page: ft.Page):
        # Cargar variables de entorno desde .env.dev si existe, si no, .env
        if os.path.exists('.env.dev'):
            load_dotenv('.env.dev')
        else:
            load_dotenv()

        try:
            # Obtener una sesión de base de datos
            db_session = get_db_session()
            
            # Configurar la sesión global
            set_db_session(db_session)
            
            # Crear el controlador de autenticación
            auth_controller = AuthController(db_session)
            
            # Crear la vista de login
            login_view = LoginView(page, auth_controller)
            
            # Registrar la función de limpieza para cuando se cierre la aplicación
            page.on_close = lambda _: cleanup_db_session()
            
        except Exception as e:
            print(f"Error al inicializar la aplicación: {e}")
            import traceback
            print(traceback.format_exc())
            return

    ft.app(target=init)

if __name__ == "__main__":
    main()