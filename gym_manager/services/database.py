from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from gym_manager.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
