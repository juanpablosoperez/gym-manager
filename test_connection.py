from sqlalchemy import create_engine, inspect
from gym_manager.models import Base

# URL de conexión
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/gym_manager"

try:
    # Crear el motor
    engine = create_engine(DATABASE_URL)
    
    # Probar la conexión
    with engine.connect() as connection:
        print("¡Conexión exitosa a la base de datos!")
        
        # Crear todas las tablas
        Base.metadata.create_all(engine)
        print("¡Tablas creadas exitosamente!")
        
        # Mostrar las tablas creadas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("\nTablas en la base de datos:")
        for table in tables:
            print(f"- {table}")
            
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
