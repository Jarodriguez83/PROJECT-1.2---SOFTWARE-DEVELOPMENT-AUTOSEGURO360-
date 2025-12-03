"""
main.py
Autor: Jhon Alexander Rodriguez Redondo

Punto de entrada para la aplicación FastAPI.
Define los endpoints CRUD para Usuario, Vehiculo, FichaTecnica y Compra.
"""
import datetime
from fastapi import Form, UploadFile, File # Añadir UploadFile y File
from fastapi.responses import HTMLResponse # Necesaria para la respuesta HTML
import shutil # Para manejar archivos


from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Para servir CSS (Punto K)
from starlette.requests import Request # Para recibir la petición y renderizar



from typing import List, Optional, Generator
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select

# Importar la configuración de la base de datos y los modelos
from database import create_db_and_tables, get_session
from models import (
    Usuario, UsuarioCreate, UsuarioRead, UsuarioUpdate,
    Vehiculo, VehiculoCreate, VehiculoRead, VehiculoUpdate,
    FichaTecnica, FichaTecnicaCreate, FichaTecnicaRead, FichaTecnicaUpdate,
    Compra, CompraCreate, CompraRead,
    SQLModel # Importar SQLModel para la definición de esquemas relacionales
)

# =================================================================
# 1. Definición de Esquemas de Lectura con Relaciones
#    Necesarios para que FastAPI pueda devolver los datos completos
# =================================================================

# Esquemas de Lectura Anidados para evitar recursión
class CompraReadSimple(CompraRead):
    pass

class UsuarioReadWithCompras(UsuarioRead):
    compras: List[CompraReadSimple] = []

class FichaTecnicaReadRel(FichaTecnicaRead):
    # La ficha técnica no necesita la relación inversa aquí
    pass

class VehiculoReadWithFichaTecnica(VehiculoRead):
    ficha_tecnica: Optional[FichaTecnicaReadRel] = None
    compras: List[CompraReadSimple] = []
    
class CompraReadRel(CompraRead):
    # Definición de la compra con datos del usuario y vehículo (simple)
    pass


# =================================================================
# 2. Inicialización de la Aplicación y Evento de Inicio
# =================================================================

app = FastAPI(
    title="AutoSeguro360 - API Avanzada",
    version="1.0.0",
    description="API para la gestión de usuarios, vehículos, fichas técnicas y transacciones de compra/venta."
)
# 1. Montar la carpeta 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Inicializar el motor de templates
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    """Ejecuta la creación de la base de datos y tablas al iniciar la app."""
    create_db_and_tables()

# =================================================================
# 3. ENDPOINTS PARA USUARIO (CRUD Completo)
# =================================================================

@app.get("/", tags=["Root - Frontend"])
def homepage(request: Request):
    """
    Sirve la página de inicio (index.html). 
    Recibe el objeto 'request' para poder generar URLs relativas.
    """
    # El diccionario de contexto se pasa al template (ej. el título de la página)
    context = {
        "request": request,
        "titulo_pagina": "AUTOSEGURO 360 - PÁGINA INICIO"
    }
    return templates.TemplateResponse("index.html", context)

# =================================================================
# 3. ENDPOINTS PARA USUARIO (CRUD y Formulario)
# =================================================================

@app.post("/usuarios/", status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def create_usuario_from_form(
    session: Session = Depends(get_session),
    cedula: str = Form(...),
    nombres_completo: str = Form(...),
    celular: str = Form(...),
    email: str = Form(...),
    edad: int = Form(...),
    categoria_licencia: str = Form("0"),
    foto_perfil: Optional[UploadFile] = File(None) # 🚨 CLAVE: Recibe el archivo
):
    """Crea un nuevo Usuario en la base de datos a partir de un formulario HTML, manejando la carga de archivos multimedia."""
    
    # --- Manejo de la URL Multimedia ---
    foto_url = None
    
    if foto_perfil and foto_perfil.filename:
        # 🚨 SIMULACIÓN DE SUBIDA A SUPABASE (Punto H)
        file_extension = foto_perfil.filename.split('.')[-1]
        unique_filename = f"perfil_{cedula}_{datetime.now().timestamp()}.{file_extension}"
        
        # Asignamos la URL simulada que Supabase daría
        foto_url = f"https://supabase.storage.io/public/perfiles/{unique_filename}"
        
    # 1. Crear el objeto UsuarioCreate a partir de los datos del formulario
    usuario_data = {
        "cedula": cedula,
        "nombres_completo": nombres_completo,
        "celular": celular,
        "email": email,
        "edad": edad,
        "categoria_licencia": categoria_licencia,
        "foto_perfil_url": foto_url # Usamos la URL generada o None
    }
    
    try:
        usuario_create = UsuarioCreate(**usuario_data)
        db_usuario = Usuario.model_validate(usuario_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la validación de datos: {e}")

    # 2. Comprobar si ya existe
    existing_user = session.get(Usuario, db_usuario.cedula)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario con cédula {db_usuario.cedula} ya existe."
        )

    # 3. Almacenar en la DB
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    
    # 4. Devolver una respuesta HTML
    return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Registro Exitoso</title>
            <link rel="stylesheet" href="{app.url_path_for('static', path='/style.css')}">
        </head>
        <body>
            <header><h1>Registro Exitoso</h1></header>
            <main class="contenedor-formulario">
                <p>✅ El usuario con cédula <strong>{db_usuario.cedula}</strong> ha sido registrado correctamente.</p>
                <p>Nombre: {db_usuario.nombres_completo}</p>
                {f'<p>URL Multimedia: <a href="{db_usuario.foto_perfil_url}" target="_blank">Ver Foto</a></p>' if db_usuario.foto_perfil_url else ''}
                <p><a href="/usuarios/registro">Registrar otro usuario</a></p>
                <p><a href="/">Volver al Inicio</a></p>
            </main>
        </body>
        </html>
    """, status_code=status.HTTP_201_CREATED)

@app.get("/usuarios/registro", tags=["Usuarios - Frontend"])
def get_registro_usuario(request: Request):
    """Muestra el formulario HTML para el registro de un nuevo usuario."""
    return templates.TemplateResponse("usuario.html", {"request": request, "titulo_pagina": "Registrar Usuario"})

# =================================================================
# 4. ENDPOINTS PARA VEHÍCULO (CRUD Completo)
# =================================================================

@app.post("/vehiculos/", response_model=VehiculoRead, status_code=status.HTTP_201_CREATED, tags=["Vehiculos"])
def create_vehiculo(vehiculo: VehiculoCreate, session: Session = Depends(get_session)):
    """Crea un nuevo Vehículo. La Placa es la clave primaria."""
    db_vehiculo = Vehiculo.model_validate(vehiculo)
    
    # Comprobar si ya existe un vehículo con esa placa
    existing_vehiculo = session.get(Vehiculo, db_vehiculo.placa)
    if existing_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vehículo con placa {db_vehiculo.placa} ya existe."
        )

    session.add(db_vehiculo)
    session.commit()
    session.refresh(db_vehiculo)
    return db_vehiculo

@app.get("/vehiculos/{placa}", response_model=VehiculoReadWithFichaTecnica, tags=["Vehiculos"])
def read_vehiculo(placa: str, session: Session = Depends(get_session)):
    """Obtiene un Vehículo específico por su Placa, incluyendo su Ficha Técnica y Compras."""
    vehiculo = session.get(Vehiculo, placa)
    if not vehiculo or vehiculo.estado == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado o inactivo.")
    return vehiculo

@app.get("/vehiculos/", response_model=List[VehiculoRead], tags=["Vehiculos"])
def read_vehiculos(session: Session = Depends(get_session)):
    """Obtiene una lista de todos los Vehículos activos."""
    statement = select(Vehiculo).where(Vehiculo.estado == True)
    results = session.exec(statement).all()
    return results

@app.delete("/vehiculos/{placa}", tags=["Vehiculos"])
def delete_vehiculo(placa: str, session: Session = Depends(get_session)):
    """Eliminación Lógica (Soft Delete): Marca el Vehículo como inactivo."""
    vehiculo = session.get(Vehiculo, placa)
    if not vehiculo or vehiculo.estado == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado o ya inactivo.")

    vehiculo.estado = False # Soft Delete
    session.add(vehiculo)
    session.commit()
    
    return {"message": f"Vehículo con placa {placa} ha sido marcado como inactivo."}


# =================================================================
# 5. ENDPOINTS PARA FICHA TÉCNICA (Relación 1:1)
# =================================================================

@app.post("/fichas_tecnicas/", response_model=FichaTecnicaRead, status_code=status.HTTP_201_CREATED, tags=["Ficha Tecnica"])
def create_ficha_tecnica(ficha: FichaTecnicaCreate, session: Session = Depends(get_session)):
    """
    Crea la Ficha Técnica para un vehículo existente. 
    Requiere que la 'vehiculo_placa' exista y no tenga ya una ficha.
    """
    # 1. Verificar si el vehículo existe
    vehiculo = session.get(Vehiculo, ficha.vehiculo_placa)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehículo con placa {ficha.vehiculo_placa} no encontrado.")
        
    # 2. Verificar si ya tiene una ficha (Relación 1:1)
    if vehiculo.ficha_tecnica:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este vehículo ya tiene una Ficha Técnica asociada.")

    db_ficha = FichaTecnica.model_validate(ficha)
    session.add(db_ficha)
    session.commit()
    session.refresh(db_ficha)
    return db_ficha

@app.patch("/fichas_tecnicas/{placa}", response_model=FichaTecnicaRead, tags=["Ficha Tecnica"])
def update_ficha_tecnica(placa: str, ficha_update: FichaTecnicaUpdate, session: Session = Depends(get_session)):
    """Actualiza la Ficha Técnica de un Vehículo por su Placa."""
    # Como la Placa es la PK/FK, podemos buscar directamente
    ficha = session.get(FichaTecnica, placa)
    if not ficha:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ficha Técnica no encontrada para la placa {placa}.")

    # Aplicar la actualización parcial
    update_data = ficha_update.model_dump(exclude_unset=True)
    ficha.model_validate(update_data, update=True)
    
    session.add(ficha)
    session.commit()
    session.refresh(ficha)
    return ficha

# =================================================================
# 6. ENDPOINTS PARA COMPRA (Transacciones N:M)
# =================================================================

@app.post("/compras/", response_model=CompraRead, status_code=status.HTTP_201_CREATED, tags=["Compras"])
def create_compra(compra: CompraCreate, session: Session = Depends(get_session)):
    """
    Registra una nueva Transacción de Compra. 
    Requiere que el Usuario (comprador_cedula) y el Vehículo (vehiculo_placa) existan.
    """
    # 1. Verificar existencia del Usuario
    usuario = session.get(Usuario, compra.comprador_cedula)
    if not usuario or usuario.estado == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Usuario (Comprador) con cédula {compra.comprador_cedula} no existe o está inactivo."
        )

    # 2. Verificar existencia del Vehículo
    vehiculo = session.get(Vehiculo, compra.vehiculo_placa)
    if not vehiculo or vehiculo.estado == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vehículo con placa {compra.vehiculo_placa} no existe o está inactivo."
        )

    db_compra = Compra.model_validate(compra)
    session.add(db_compra)
    session.commit()
    session.refresh(db_compra)
    return db_compra

@app.get("/compras/", response_model=List[CompraRead], tags=["Compras"])
def read_compras(session: Session = Depends(get_session)):
    """Obtiene todas las transacciones de compra registradas."""
    statement = select(Compra)
    results = session.exec(statement).all()
    return results

@app.get("/compras/{compra_id}", response_model=CompraRead, tags=["Compras"])
def read_compra(compra_id: int, session: Session = Depends(get_session)):
    """Obtiene una transacción de Compra específica por su ID."""
    compra = session.get(Compra, compra_id)
    if not compra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción de Compra no encontrada.")
    return compra


# =================================================================
# 7. ENDPOINT RAIZ
# =================================================================

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a AutoSeguro360 - API Avanzada. Consulta /docs para ver los endpoints."}

    