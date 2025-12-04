from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import os 
import models 

#NOMBRE DEL ARCHIVO DE LA BASE DE DATOS SQLITE
SQLITE_FILE_NAME = "autoseguro360_avanzado.db"
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(
    sqlite_url, 
    echo=False, 
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    #Crea la base de datos y las tablas si no existen.
    print(f"--- CREANDO O VERIFICANDO LA BASE DE DATOS LOCAL: {SQLITE_FILE_NAME} ---")
    SQLModel.metadata.create_all(engine)


# CLAVE: Esta función ahora devuelve una sesión SÍNCRONA
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session