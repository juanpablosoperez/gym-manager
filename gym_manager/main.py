import flet as ft
from gym_manager.views.login_view import LoginView
from gym_manager.utils.navigation import init_db, navigate_to_login
from gym_manager.utils.database import get_db_session
from gym_manager.controllers.auth_controller import AuthController

def main(page: ft.Page):
    # Inicializar la base de datos
    init_db()
    
    # Configurar la página
    page.title = "Gym Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    
    # Navegar a la vista de login
    navigate_to_login(page)

if __name__ == "__main__":
    ft.app(target=main)