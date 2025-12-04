"""
database.py
Autor: Jhon Alexander Rodriguez Redondo

Configuración del motor de base de datos (SQLite) para desarrollo local.
Utiliza un motor síncrono.
"""

from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import os # Necesario para la conexión (aunque no se usa directamente)
import models 

# Nombre del archivo de base de datos local
SQLITE_FILE_NAME = "autoseguro360_avanzado.db"
# URL de conexión para SQLite (protocolo estándar)
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"

# Crear el motor de la base de datos
# CLAVE: Usamos create_engine (síncrono)
# CLAVE: connect_args es esencial para SQLite en FastAPI (multi-threading)
engine = create_engine(
    sqlite_url, 
    echo=False, 
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """
    Crea la base de datos y todas las tablas definidas en los modelos.
    """
    print(f"--- Creando o verificando la base de datos local: {SQLITE_FILE_NAME} ---")
    SQLModel.metadata.create_all(engine)


# CLAVE: Esta función ahora devuelve una sesión SÍNCRONA
def get_session() -> Generator[Session, None, None]:
    """
    Función generadora para obtener una sesión SÍNCRONA de SQLModel. 
    """
    with Session(engine) as session:
        yield session