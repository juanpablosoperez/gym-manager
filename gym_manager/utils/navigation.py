import flet as ft

# Variable global para mantener la sesión de la base de datos
db_session = None

def set_db_session(session):
    global db_session
    db_session = session

def navigate_to_login(page: ft.Page):
    global db_session
    
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
    
    # Crear y mostrar vista de login con la sesión existente
    auth_controller = AuthController(db_session)
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
    except ImportError as e:
        print(f"Error al importar HomeView: {e}")
        # Mostrar mensaje de error en la página
        page.add(ft.Text("Error al cargar la vista principal", color=ft.colors.RED))
        page.update() 