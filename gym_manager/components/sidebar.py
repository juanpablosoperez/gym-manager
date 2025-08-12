import flet as ft
from gym_manager.utils.roles import get_allowed_modules_by_role

def create_sidebar(page: ft.Page, user_role: str, on_item_selected=None):
    full_menu_items = [
        {"icon": ft.icons.DASHBOARD_OUTLINED, "text": "Dashboard", "selected_icon": ft.icons.DASHBOARD},
        {"icon": ft.icons.PEOPLE_OUTLINE, "text": "Miembros", "selected_icon": ft.icons.PEOPLE},
        {"icon": ft.icons.FITNESS_CENTER_OUTLINED, "text": "Rutinas", "selected_icon": ft.icons.FITNESS_CENTER},
        {"icon": ft.icons.PAYMENTS_OUTLINED, "text": "Pagos", "selected_icon": ft.icons.PAYMENTS},
        {"icon": ft.icons.RECEIPT_OUTLINED, "text": "Comprobantes", "selected_icon": ft.icons.RECEIPT},
        {"icon": ft.icons.ANALYTICS_OUTLINED, "text": "Estadísticas", "selected_icon": ft.icons.ANALYTICS},
        {"icon": ft.icons.CREDIT_CARD_OUTLINED, "text": "Métodos de Pago", "selected_icon": ft.icons.CREDIT_CARD},
        {"icon": ft.icons.ADMIN_PANEL_SETTINGS_OUTLINED, "text": "Usuarios", "selected_icon": ft.icons.ADMIN_PANEL_SETTINGS},
        {"icon": ft.icons.BACKUP_OUTLINED, "text": "Backup", "selected_icon": ft.icons.BACKUP},
    ]

    allowed_texts = set(get_allowed_modules_by_role(user_role))
    menu_items = [item for item in full_menu_items if item["text"] in allowed_texts]

    is_expanded = True
    selected_index = 0

    def build_nav_item(icon, selected_icon, text):
        return ft.NavigationRailDestination(
            icon=icon,
            selected_icon=selected_icon,
            label=text if is_expanded else "",
            padding=ft.padding.symmetric(vertical=5),
        )

    def toggle_nav_rail(e):
        nonlocal is_expanded
        is_expanded = not is_expanded
        e.control.selected = is_expanded
        nav_rail.extended = is_expanded
        
        # Actualizar las etiquetas de los items
        for i, item in enumerate(menu_items):
            nav_items[i].label = item["text"] if is_expanded else ""
        
        page.update()

    def on_nav_change(e):
        nonlocal selected_index
        selected_index = e.control.selected_index
        if on_item_selected:
            on_item_selected(selected_index)

    toggle_button = ft.IconButton(
        icon=ft.icons.MENU,
        selected_icon=ft.icons.MENU_OPEN,
        icon_color=ft.colors.BLUE,
        selected=is_expanded,
        on_click=toggle_nav_rail,
        tooltip="Expandir/Colapsar menú",
    )

    nav_items = [
        build_nav_item(
            icon=item["icon"],
            selected_icon=item["selected_icon"],
            text=item["text"],
        ) for item in menu_items
    ]

    nav_rail = ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=200,
        leading=toggle_button,
        group_alignment=-0.9,
        destinations=nav_items,
        extended=is_expanded,
        on_change=on_nav_change,
        bgcolor=ft.colors.WHITE,
    )

    return ft.Container(
        content=nav_rail,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.BLACK12,
            offset=ft.Offset(2, 0),
        ),
        border=ft.border.only(right=ft.BorderSide(1, ft.colors.GREY_300)),
    ) 