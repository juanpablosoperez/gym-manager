import flet as ft
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from gym_manager.views.login_view import LoginView
from gym_manager.controllers.auth_controller import AuthController
from gym_manager.models import Base
from gym_manager.utils.navigation import set_db_session
import os
from dotenv import load_dotenv

def main():
    def init(page: ft.Page):
        # Cargar variables de entorno
        load_dotenv()
        
        # Configuración de la base de datos MySQL
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')  # Asegúrate de que esta es tu contraseña
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME', 'gym_manager')
        
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"Conectando a la base de datos: {DATABASE_URL}")
        
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=True  # Esto mostrará todas las consultas SQL
        )
        
        try:
            # Probar la conexión
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
                count = result.scalar()
                print(f"Conexión exitosa. Total de usuarios en la base de datos: {count}")
                
                # Mostrar un usuario de ejemplo
                result = conn.execute(text("SELECT * FROM usuarios LIMIT 1"))
                user = result.fetchone()
                if user:
                    # Convertir el resultado a un diccionario usando el método correcto
                    user_dict = {key: value for key, value in zip(result.keys(), user)}
                    print(f"Usuario de ejemplo encontrado:")
                    print(f"  ID: {user_dict.get('id_usuario')}")
                    print(f"  Nombre: {user_dict.get('nombre')}")
                    print(f"  Rol: {user_dict.get('rol')}")
                    print(f"  Estado: {user_dict.get('estado')}")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            import traceback
            print(traceback.format_exc())
            return
        
        # Crear el controlador de autenticación
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()
        
        # Establecer la sesión de la base de datos
        set_db_session(db_session)

        # Iniciar la vista de login
        auth_controller = AuthController(db_session)
        login_view = LoginView(page, auth_controller)

    ft.app(target=init)

if __name__ == "__main__":
    main()

