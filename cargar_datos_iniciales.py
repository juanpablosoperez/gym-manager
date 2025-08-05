from gym_manager.utils.database import get_db_session
from sqlalchemy import text
from datetime import datetime

def cargar_datos():
    session = get_db_session()
    try:
        # Insertar rutina de ejemplo
        session.execute(text("""
            INSERT INTO rutinas (nombre, descripcion, nivel_dificultad, fecha_creacion, fecha_horario)
            VALUES ('Rutina Básica', 'Rutina para principiantes', 'Baja', :fecha_creacion, :fecha_horario)
        """), {
            'fecha_creacion': datetime.now(),
            'fecha_horario': datetime.now()
        })
        
        # Insertar método de pago de ejemplo
        session.execute(text("""
            INSERT INTO metodos_pago (descripcion, estado)
            VALUES ('Efectivo', 1), ('Tarjeta', 1)
        """))
        
        # Insertar cuota mensual de ejemplo
        session.execute(text("""
            INSERT INTO cuota_mensual (monto, fecha_actualizacion, activo)
            VALUES (5000, :fecha_actualizacion, 1)
        """), {
            'fecha_actualizacion': datetime.now()
        })
        
        # Insertar usuario admin (miembro)
        session.execute(text("""
            INSERT INTO miembros (nombre, apellido, documento, fecha_nacimiento, genero, correo_electronico, estado, tipo_membresia, direccion, telefono, fecha_registro, informacion_medica, id_rutina)
            VALUES ('Admin', 'Principal', '00000000', '1990-01-01', 'Otro', 'admin@gym.com', 1, 'Admin', 'Oficina', '123456789', :fecha_registro, 'Sin condiciones', 1)
        """), {
            'fecha_registro': datetime.now()
        })
        
        # Insertar pago de ejemplo para admin
        session.execute(text("""
            INSERT INTO pagos (fecha_pago, monto, referencia, estado, id_miembro, id_metodo_pago)
            VALUES (:fecha_pago, 5000, 'Pago inicial', 1, 1, 1)
        """), {
            'fecha_pago': datetime.now()
        })
        
        # Insertar comprobante de pago de ejemplo
        session.execute(text("""
            INSERT INTO comprobantes_pago (contenido, fecha_emision, id_pago)
            VALUES (:contenido, :fecha_emision, 1)
        """), {
            'contenido': b'Comprobante de ejemplo',
            'fecha_emision': datetime.now()
        })
        
        # Insertar relación miembro-rutina
        session.execute(text("""
            INSERT INTO miembro_rutina (id_miembro, id_rutina)
            VALUES (1, 1)
        """))
        
        session.commit()
        print("¡Datos iniciales cargados exitosamente!")
    except Exception as e:
        session.rollback()
        print(f"Error al cargar datos: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    cargar_datos() 