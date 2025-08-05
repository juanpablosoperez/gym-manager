from gym_manager.utils.database import get_db_session
from sqlalchemy import text

def reset_database():
    session = get_db_session()
    try:
        # Desactivar restricciones de clave foránea
        session.execute(text('SET FOREIGN_KEY_CHECKS=0'))
        
        # Eliminar tablas existentes
        session.execute(text('DROP TABLE IF EXISTS alembic_version'))
        session.execute(text('DROP TABLE IF EXISTS comprobantes_pago'))
        session.execute(text('DROP TABLE IF EXISTS cuota_mensual'))
        session.execute(text('DROP TABLE IF EXISTS metodos_pago'))
        session.execute(text('DROP TABLE IF EXISTS miembro_rutina'))
        session.execute(text('DROP TABLE IF EXISTS miembros'))
        session.execute(text('DROP TABLE IF EXISTS pagos'))
        session.execute(text('DROP TABLE IF EXISTS rutinas'))
        
        # Crear tabla rutinas
        session.execute(text('''
            CREATE TABLE IF NOT EXISTS rutinas (
                id_rutina INT NOT NULL AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                documento_rutina LONGBLOB,
                nivel_dificultad VARCHAR(20) NOT NULL,
                fecha_creacion DATETIME,
                fecha_horario DATETIME,
                PRIMARY KEY (id_rutina)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        '''))
        
        # Crear tabla miembros
        session.execute(text('''
            CREATE TABLE IF NOT EXISTS miembros (
                id_miembro INT NOT NULL AUTO_INCREMENT,
                nombre VARCHAR(50) NOT NULL,
                apellido VARCHAR(50) NOT NULL,
                documento VARCHAR(20) NOT NULL,
                fecha_nacimiento DATE NOT NULL,
                genero VARCHAR(10) NOT NULL,
                correo_electronico VARCHAR(100) NOT NULL,
                estado BOOLEAN NOT NULL,
                tipo_membresia VARCHAR(20) NOT NULL,
                direccion VARCHAR(200),
                telefono VARCHAR(20),
                fecha_registro DATETIME NOT NULL,
                informacion_medica TEXT,
                id_rutina INT,
                PRIMARY KEY (id_miembro),
                UNIQUE KEY documento (documento),
                UNIQUE KEY correo_electronico (correo_electronico),
                KEY fk_miembro_rutina (id_rutina),
                CONSTRAINT fk_miembro_rutina FOREIGN KEY (id_rutina) REFERENCES rutinas (id_rutina)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        '''))
        
        # Crear tabla metodos_pago
        session.execute(text('''
            CREATE TABLE IF NOT EXISTS metodos_pago (
                id_metodo_pago INT NOT NULL AUTO_INCREMENT,
                descripcion VARCHAR(50) NOT NULL,
                estado BOOLEAN NOT NULL,
                PRIMARY KEY (id_metodo_pago)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        '''))
        
        # Crear tabla pagos
        session.execute(text('''
            CREATE TABLE IF NOT EXISTS pagos (
                id_pago INT NOT NULL AUTO_INCREMENT,
                fecha_pago DATETIME NOT NULL,
                monto FLOAT NOT NULL,
                referencia VARCHAR(50),
                estado BOOLEAN NOT NULL,
                id_miembro INT NOT NULL,
                id_metodo_pago INT NOT NULL,
                PRIMARY KEY (id_pago),
                KEY id_miembro (id_miembro),
                KEY id_metodo_pago (id_metodo_pago),
                CONSTRAINT pagos_ibfk_1 FOREIGN KEY (id_miembro) REFERENCES miembros (id_miembro),
                CONSTRAINT pagos_ibfk_2 FOREIGN KEY (id_metodo_pago) REFERENCES metodos_pago (id_metodo_pago)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        '''))
        
        # Crear tabla comprobantes_pago
        session.execute(text('''
            CREATE TABLE IF NOT EXISTS comprobantes_pago (
                id_comprobante INT NOT NULL AUTO_INCREMENT,
                contenido BLOB NOT NULL,
                fecha_emision DATETIME NOT NULL,
                id_pago INT NOT NULL,
                PRIMARY KEY (id_comprobante),
                UNIQUE KEY id_pago (id_pago),
                CONSTRAINT comprobantes_pago_ibfk_1 FOREIGN KEY (id_pago) REFERENCES pagos (id_pago)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        '''))
        
        # Crear tabla cuota_mensual
        session.execute(text('''
            CREATE TABLE IF NOT EXISTS cuota_mensual (
                id_cuota INT NOT NULL AUTO_INCREMENT,
                monto FLOAT NOT NULL,
                fecha_actualizacion DATETIME NOT NULL,
                activo INT,
                PRIMARY KEY (id_cuota)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        '''))
        
        # Crear tabla miembro_rutina
        session.execute(text('''
            CREATE TABLE IF NOT EXISTS miembro_rutina (
                id_miembro INT NOT NULL,
                id_rutina INT NOT NULL,
                PRIMARY KEY (id_miembro,id_rutina),
                KEY id_rutina (id_rutina),
                CONSTRAINT miembro_rutina_ibfk_1 FOREIGN KEY (id_miembro) REFERENCES miembros (id_miembro),
                CONSTRAINT miembro_rutina_ibfk_2 FOREIGN KEY (id_rutina) REFERENCES rutinas (id_rutina)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        '''))
        
        # Reactivar restricciones de clave foránea
        session.execute(text('SET FOREIGN_KEY_CHECKS=1'))
        
        session.commit()
        print("Base de datos reiniciada exitosamente")
    except Exception as e:
        session.rollback()
        print(f"Error al reiniciar la base de datos: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    reset_database() 