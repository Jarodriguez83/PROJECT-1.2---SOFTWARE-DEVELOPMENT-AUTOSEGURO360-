from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import get_session, engine
import models  # Importa todos los modelos para crear las tablas

app = FastAPI()

# Configuración de templates y archivos estáticos
templates = Jinja2Templates(directory="templates")

# 🧱 Crear las tablas
models.SQLModel.metadata.create_all(engine)

# Ruta principal
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "titulo": "Bienvenido a AutoSeguro360"}
    )
