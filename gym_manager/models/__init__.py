from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crear la base declarativa
Base = declarative_base()

# Importar todos los modelos
from gym_manager.models.user import Usuario
from gym_manager.models.member import Miembro
from gym_manager.models.routine import Rutina
from gym_manager.models.payment_method import MetodoPago
from gym_manager.models.payment import Pago
from gym_manager.models.payment_receipt import ComprobantePago
from gym_manager.models.backup import Backup
from gym_manager.models.monthly_fee import CuotaMensual

__all__ = [
    'Base',
    'Usuario',
    'Miembro',
    'Pago',
    'MetodoPago',
    'Rutina',
    'ComprobantePago',
    'Backup',
    'CuotaMensual'
]

def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
