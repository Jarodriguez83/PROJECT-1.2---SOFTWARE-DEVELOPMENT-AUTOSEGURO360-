"""
database.py
Autor: Jhon Alexander Rodriguez Redondo

Configuración del motor de base de datos para PostgreSQL (Render/Supabase)
usando variables de entorno y el driver asíncrono 'asyncpg'.

Este código es robusto para el despliegue: lee la variable DATABASE_URL de Render
y usa el pool de conexiones optimizado.
"""

from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import os
import models 

# 🚨 CLAVE CRÍTICO: Leer la URL de PostgreSQL desde una variable de entorno (DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL") 

# --- Configuración de Desarrollo Local (si es necesario) ---
# Si ejecutas la aplicación localmente y la variable DATABASE_URL no está seteada, 
# se usará esta URL de ejemplo. DEBES reemplazar [YOUR_PASSWORD_AQUÍ] por tu contraseña real.
if not DATABASE_URL:
    print("ADVERTENCIA: Usando URL de base de datos de desarrollo por defecto.")
    # Usamos el formato 'postgresql+asyncpg://' para desarrollo local
    HOST_DOMAIN = "db.okuotijfayaoecerimfi.supabase.co"
    DATABASE_URL = f"postgresql+asyncpg://postgres:[YOUR_PASSWORD_AQUÍ]@{HOST_DOMAIN}:5432/postgres" 
# ----------------------------------------------------------

# El motor debe configurarse para PostgreSQL
engine = create_engine(
    # La URL ahora usa el esquema 'postgresql+asyncpg' (ya sea desde el entorno o el fallback)
    url=DATABASE_URL, 
    echo=False,
    # Ajustamos el Pool de Conexiones a un valor seguro (máximo 15 permitido en plan Nano)
    pool_size=12, 
    max_overflow=0 
)

def create_db_and_tables():
    """
    Crea la base de datos y todas las tablas definidas en los modelos.
    Esto se ejecuta al inicio de la aplicación para asegurar que la DB esté lista.
    """
    print(f"--- Creando o verificando tablas en PostgreSQL (AsyncPG) ---")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Función generadora para obtener una sesión de SQLModel. 
    Se utiliza como dependencia en los endpoints de FastAPI.
    """
    with Session(engine) as session:
        yield session