from sqlalchemy.orm import Session
from gym_manager.models.user import Usuario
import bcrypt

class AuthController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def authenticate_user(self, nombre: str, contraseña: str) -> tuple[bool, str]:
        try:
            print(f"Intentando autenticar usuario: {nombre}")
            
            # Primero verificamos si podemos hacer una consulta simple
            total_users = self.db_session.query(Usuario).count()
            print(f"Total de usuarios en la base de datos: {total_users}")
            
            # Hacemos la consulta y mostramos los resultados
            user = self.db_session.query(Usuario).filter(
                Usuario.nombre == nombre,
                Usuario.estado == True
            ).first()
            
            print(f"Resultado de la consulta: {user}")
            
            if user:
                print(f"Usuario encontrado: ID={user.id_usuario}, Nombre={user.nombre}, Rol={user.rol}")
                print(f"Contraseña ingresada: {contraseña}")
                print(f"Contraseña en BD: {user.contraseña}")
                
                # Verificar la contraseña usando bcrypt
                if bcrypt.checkpw(contraseña.encode('utf-8'), user.contraseña.encode('utf-8')):
                    print("¡Contraseña correcta!")
                    return True, user.rol
                else:
                    print("Contraseña incorrecta")
            else:
                print("Usuario no encontrado")
                
            return False, ""
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            import traceback
            print(traceback.format_exc())
            return False, "" 