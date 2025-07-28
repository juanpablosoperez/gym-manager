from gym_manager.migrations.remove_id_miembro_rutinas import migrate as remove_id_miembro

def run_migrations():
    """
    Ejecuta todas las migraciones pendientes
    """
    print("Ejecutando migraciones...")
    
    # Ejecutar migración para eliminar id_miembro de rutinas
    try:
        remove_id_miembro()
        print("Migración completada exitosamente")
    except Exception as e:
        print(f"Error durante la migración: {str(e)}")

if __name__ == "__main__":
    run_migrations() 