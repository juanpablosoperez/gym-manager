from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Importar todos los modelos
from gym_manager.models.base import Base
from gym_manager.models.user import Usuario
from gym_manager.models.member import Miembro
from gym_manager.models.routine import Rutina
from gym_manager.models.payment_method import MetodoPago
from gym_manager.models.payment import Pago
from gym_manager.models.payment_receipt import ComprobantePago

__all__ = [
    'Base',
    'Usuario',
    'Miembro',
    'Pago',
    'MetodoPago',
    'Rutina'
]

def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
