"""
database.py
Autor: Jhon Alexander Rodriguez Redondo

Configuración del motor de base de datos (SQLite) y provisión de sesiones para FastAPI.
"""

from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import models 

# Nombre del archivo de base de datos
SQLITE_FILE_NAME = "autoseguro360_avanzado.db"
# URL de conexión para SQLite
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"

# Crear el motor de la base de datos
# echo=False para evitar que imprima todas las sentencias SQL en la consola
# connect_args={"check_same_thread": False} es necesario para trabajar con SQLite y FastAPI
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """
    Crea la base de datos y todas las tablas definidas en los modelos.
    Importante: Esto borra cualquier dato existente si la estructura cambia,
    a menos que uses migraciones (fuera del alcance de este paso).
    """
    print(f"--- Creando o verificando la base de datos: {SQLITE_FILE_NAME} ---")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Función generadora para obtener una sesión de SQLModel. 
    Se utiliza como dependencia en los endpoints de FastAPI.
    """
    with Session(engine) as session:
        yield session

# Nota importante: Asegúrate de que el archivo 'models.py' esté completo y sin errores de sintaxis
# antes de ejecutar la aplicación, ya que esta función depende de la metadata de SQLModel.