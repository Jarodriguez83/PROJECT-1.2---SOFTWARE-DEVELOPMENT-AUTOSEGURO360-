"""
database.py
Autor: Jhon Alexander Rodriguez Redondo

Configuración del motor de base de datos para PostgreSQL (Render/Supabase)
usando variables de entorno y el driver asíncrono 'psycopg'.
"""

from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import os
import models 

# 🚨 CLAVE CRÍTICO: Leer la URL de PostgreSQL desde una variable de entorno (DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL") 

# --- Configuración de Desarrollo Local (si es necesario) ---
# Si ejecutas la aplicación localmente y la variable DATABASE_URL no está seteada, 
# se usará esta URL de ejemplo.
if not DATABASE_URL:
    print("ADVERTENCIA: Usando URL de base de datos de desarrollo por defecto.")
    # 🚨 NOTA: La URL AHORA VUELVE A SER LA ESTÁNDAR 'postgresql://'
    # La especificación del driver se hace abajo en create_engine
    HOST_DOMAIN = "db.okuotijfayaoecerimfi.supabase.co"
    DATABASE_URL = f"postgresql://postgres:[YOUR_PASSWORD_AQUÍ]@{HOST_DOMAIN}:5432/postgres" 
# ----------------------------------------------------------

# 🚨 DETERMINAR DRIVER NAME: Usaremos 'postgresql+psycopg'
# Esto es lo que Render usará para conectar el driver correcto.
DRIVER_NAME = "postgresql+psycopg"

# El motor debe configurarse para PostgreSQL
engine = create_engine(
    # 🚨 CAMBIO CLAVE: Usamos el argumento 'drivername' para forzar el uso de psycopg
    url=DATABASE_URL, 
    drivername=DRIVER_NAME,
    echo=False,
    # Ajustamos el Pool de Conexiones para no exceder el límite Nano (15)
    pool_size=12, 
    max_overflow=0 
)

def create_db_and_tables():
    """
    Crea la base de datos y todas las tablas definidas en los modelos.
    Esto se ejecuta al inicio de la aplicación para asegurar que la DB esté lista.
    """
    print(f"--- Creando o verificando tablas en PostgreSQL ---")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Función generadora para obtener una sesión de SQLModel. 
    Se utiliza como dependencia en los endpoints de FastAPI.
    """
    with Session(engine) as session:
        yield session