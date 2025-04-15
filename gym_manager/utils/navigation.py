import flet as ft

def navigate_to_login(page: ft.Page):
    from gym_manager.views.login_view import LoginView
    from gym_manager.controllers.auth_controller import AuthController
    
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
    
    # Crear y mostrar vista de login
    auth_controller = AuthController(None)
    LoginView(page, auth_controller)

def navigate_to_home(page: ft.Page, user_rol: str, user_name: str):
    from gym_manager.views.home_view import HomeView
    
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
    
    # Crear y mostrar vista de home
    HomeView(page, user_rol, user_name) 