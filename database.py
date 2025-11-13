from sqlmodel import create_engine, SQLModel, Session
from models import Vehiculo, Usuario, DetalleSeguroVehiculo # Importar todos los modelos para la metadata

# Nombre del archivo de base de datos
SQLITE_FILE_NAME = "autoseguro360.db"
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    """Crea la base de datos y todas las tablas definidas en los modelos."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Función generadora para obtener una sesión de SQLModel. Usada como dependencia en FastAPI."""
    with Session(engine) as session:
        yield session

