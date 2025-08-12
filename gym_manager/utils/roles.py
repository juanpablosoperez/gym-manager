from typing import List


ADMIN_ROLE = "admin"


def get_allowed_modules_by_role(user_role: str) -> List[str]:
    """Return the list of visible modules for the given role (by menu text).

    Non-admin roles are restricted to: Dashboard, Miembros, Pagos, Comprobantes.
    Admins can see all modules (the caller will typically pass the full list to compare).
    """
    if (user_role or "").lower() == ADMIN_ROLE:
        # Admin: caller should not filter; return empty means no filtering needed
        return [
            "Dashboard",
            "Miembros",
            "Rutinas",
            "Pagos",
            "Comprobantes",
            "Estadísticas",
            "Métodos de Pago",
            "Usuarios",
            "Backup",
        ]
    # Default: restricted modules only
    return [
        "Dashboard",
        "Miembros",
        "Pagos",
        "Comprobantes",
    ]


def is_module_allowed(user_role: str, module_text: str) -> bool:
    """Check if the module (by menu text) is allowed for the given role."""
    allowed = get_allowed_modules_by_role(user_role)
    return module_text in allowed


