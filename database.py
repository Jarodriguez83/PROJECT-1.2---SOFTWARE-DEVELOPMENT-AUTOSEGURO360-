# database.py
from sqlmodel import SQLModel, create_engine, Session

# ---------------------------------------------------------
# CONFIGURACIÓN DEL MOTOR DE BASE DE DATOS
# ---------------------------------------------------------

DATABASE_URL = "sqlite:///database.db"   # Puedes cambiarlo a PostgreSQL luego

engine = create_engine(
    DATABASE_URL,
    echo=True,        # Muestra las consultas en consola (útil en desarrollo)
    connect_args={"check_same_thread": False}  # Necesario para SQLite
)

# ---------------------------------------------------------
# CREAR TODAS LAS TABLAS
# ---------------------------------------------------------

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ---------------------------------------------------------
# DEPENDENCIA — SESIÓN DE BASE DE DATOS
# ---------------------------------------------------------

def get_session():
    with Session(engine) as session:
        yield session
