from gym_manager.services.database import Base, engine
from gym_manager.models.monthly_fee import CuotaMensual
from datetime import datetime

def init_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Verificar si ya existe una cuota mensual
    from sqlalchemy.orm import Session
    from gym_manager.services.database import SessionLocal
    
    db = SessionLocal()
    try:
        existing_fee = db.query(CuotaMensual).filter_by(activo=1).first()
        if not existing_fee:
            # Crear una cuota mensual inicial
            initial_fee = CuotaMensual(
                monto=0.00,  # Monto inicial en 0
                fecha_actualizacion=datetime.now(),
                activo=1
            )
            db.add(initial_fee)
            db.commit()
            print("Cuota mensual inicial creada")
        else:
            print("Ya existe una cuota mensual activa")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 