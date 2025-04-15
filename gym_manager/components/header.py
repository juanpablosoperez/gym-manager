import flet as ft

def create_header(page: ft.Page, user_name: str, user_role: str, on_logout=None):
    return ft.Container(
        content=ft.Row(
            controls=[
                # Logo y nombre del sistema
                ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.FITNESS_CENTER_ROUNDED,
                            size=24,
                            color=ft.colors.WHITE,
                        ),
                        ft.Text(
                            "Gym Manager",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                        ),
                    ],
                    spacing=10,
                ),
                
                # Espaciador
                ft.Container(expand=True),
                
                # Información del usuario y botón de logout
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        user_name,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.WHITE,
                                    ),
                                    ft.Text(
                                        f"Rol: {user_role}",
                                        size=12,
                                        color=ft.colors.WHITE70,
                                    ),
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ),
                        ft.IconButton(
                            icon=ft.icons.LOGOUT_ROUNDED,
                            icon_color=ft.colors.WHITE,
                            tooltip="Cerrar sesión",
                            on_click=on_logout,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=ft.colors.BLUE,
        padding=ft.padding.all(15),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.BLACK12,
            offset=ft.Offset(0, 2),
        ),
    ) 