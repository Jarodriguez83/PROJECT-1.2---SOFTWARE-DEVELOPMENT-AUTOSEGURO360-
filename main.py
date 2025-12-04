#LIBRERÍAS PARA EL USO DE SUPABASE
from datetime import datetime 
import shutil 
from fastapi.params import Query
from httpx import request
from sqlalchemy import or_
from supabase import create_client, Client # NUEVO: Cliente Supabase
from starlette.requests import Request # Asegúrate de tener esta importación

from fastapi import Form, UploadFile, File # Añadir UploadFile y File
from fastapi.responses import HTMLResponse # Necesaria para la respuesta HTML
import shutil # Para manejar archivos

#LIBRERÍAS PARA EL USO DE TEMPLATES CON FASTAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Para servir CSS (Punto K)
from starlette.requests import Request # Para recibir la petición y renderizar


#LIBRERÍAS ESTÁNDAR PARA FASTAPI Y SQLMODEL
from typing import List, Optional, Generator
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select

#IMPORTACIÓN DE MÓDULOS PROPIOS Y MODELOS
from database import create_db_and_tables, get_session
from models import (
    Usuario, UsuarioCreate, UsuarioRead, UsuarioUpdate,
    Vehiculo, VehiculoCreate, VehiculoRead, VehiculoUpdate,
    FichaTecnica, FichaTecnicaCreate, FichaTecnicaRead, FichaTecnicaUpdate,
    Compra, CompraCreate, CompraRead,
    SQLModel # Importar SQLModel para la definición de esquemas relacionales
)

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

app = FastAPI(
    title="AutoSeguro360 - API Avanzada",
    version="1.0.0",
    description="API para la gestión de usuarios, vehículos, fichas técnicas y transacciones de compra/venta."
)
# MONTAR LA CARPETA DE ARCHIVOS ESTÁTICOS (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# INICIALIZAR LOS TEMPLATES
templates = Jinja2Templates(directory="templates")

# CONFIGURACIÓN DE SUPABASE 
SUPABASE_URL = "https://okuotijfayaoecerimfi.supabase.co" 
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rdW90aWpmYXlhb2VjZXJpbWZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3OTg1OTMsImV4cCI6MjA4MDM3NDU5M30.8SstgKcCZs3CbcZSd0KEH4FQ7VBEnLR3t5RJeBzvsxk" 
SUPABASE_BUCKET_NAME = "IMG" 

# CLIENTE SUPABASE INICIALIZADO
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.on_event("startup")
def on_startup():
    """Ejecuta la creación de la base de datos y tablas al iniciar la app."""
    create_db_and_tables()


@app.get("/", tags=["Root - Frontend"])
def homepage(
    request: Request, 
    session: Session = Depends(get_session),
    busqueda_texto: Optional[str] = Query(None, description="Texto de búsqueda libre (Marca, Línea)"),
    anio_filtro: Optional[str] = Query(None, description="Filtrar por año de modelo"),
    ncap_filtro: Optional[str] = Query(None, description="Filtrar por calificación Latin NCAP mínima (0-5)"),
    precio_max: Optional[str] = Query(None, description="Filtrar por precio máximo"),
):
    """
    Sirve la página de inicio (index.html) con el explorador de vehículos, 
    aplicando filtros de búsqueda desde la URL.
    """
    
    # LÓGICA DE CONVERSIÓN Y VALIDACIÓN NUMÉRICA PARA EVITAR ERRORES DE PARSEO
    
    anio_filtro_num: Optional[int] = None
    ncap_filtro_num: Optional[int] = None
    precio_max_num: Optional[float] = None
    
    try:
        #CONVERTIR 
        if anio_filtro and anio_filtro != "":
            anio_filtro_num = int(anio_filtro)
            
        # Intentamos convertir la calificación NCAP si no está vacía
        if ncap_filtro and ncap_filtro != "":
            ncap_filtro_num = int(ncap_filtro)
            
        # Intentamos convertir el precio máximo si no está vacío
        if precio_max and precio_max != "":
            precio_max_num = float(precio_max)
            
    except ValueError:
        # Si la conversión a int/float falla (ej: el usuario escribe "hola"), lanzamos un error claro.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de formato: Los filtros de Año, NCAP y Precio Máximo deben ser números válidos."
        )
    
    # CONSULTA BASE: VEHÍCULOS ACTIVOS
    statement = select(Vehiculo).where(Vehiculo.estado == True)
    
    # Aplicar Búsqueda por Texto (Busca en Marca O Línea)
    if busqueda_texto:
        search_term = f"%{busqueda_texto}%"
        # Usamos or_ para buscar en Marca o Línea (case-insensitive)
        statement = statement.where(or_(
            Vehiculo.marca.ilike(search_term), 
            Vehiculo.linea.ilike(search_term)
        ))
    
    # Aplicar Filtros Específicos usando las variables numéricas
    if anio_filtro_num is not None:
        statement = statement.where(Vehiculo.modelo == anio_filtro_num)
    
    if ncap_filtro_num is not None:
        statement = statement.where(Vehiculo.nivel_seguridad >= ncap_filtro_num)
        
    if precio_max_num is not None:
        statement = statement.where(Vehiculo.precio <= precio_max_num)
    
    vehicles = session.exec(statement).all()
    
    context = {
        "request": request,
        "titulo_pagina": "AutoSeguro360 - Explorador de Vehículos",
        "vehicles": vehicles, 
        # Pasamos los valores de filtro de vuelta al template para mantener la selección
        "current_search": busqueda_texto or "",
        "current_anio": anio_filtro or "",
        "current_ncap": ncap_filtro or "",
        "current_precio": precio_max or "",
    }
    return templates.TemplateResponse("index.html", context)



@app.get("/usuarios/registro", tags=["Usuarios - Frontend"])
def get_registro_usuario(request: Request):
    """Muestra el formulario HTML para el registro de un nuevo usuario."""
    context = {
        "request": request,
        "titulo_pagina": "Registro de Nuevo Usuario"
    }
    return templates.TemplateResponse("usuario.html", context)


# 3. ENDPOINTS PARA USUARIO (CRUD y Formulario)
@app.post("/usuarios/", status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
async def create_usuario_from_form(
    request: Request, # Se requiere para templates.TemplateResponse
    session: Session = Depends(get_session),
    cedula: str = Form(...),
    nombres_completo: str = Form(...),
    celular: str = Form(...),
    email: str = Form(...),
    edad: int = Form(...),
    categoria_licencia: str = Form("0"),
    foto_perfil: Optional[UploadFile] = File(None),
):
    """
    Crea un nuevo Usuario, procesa el formulario, sube la foto a Supabase, 
    y responde con el HTML de registro exitoso.
    """
    
    foto_url = None
    
    if foto_perfil and foto_perfil.filename:
        
        # PROCESO DE SUBIDA REAL A SUPABASE STORAGE
        file_extension = foto_perfil.filename.split('.')[-1]
        unique_filename = f"fotos/{cedula}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        
        try:
            #Leer el archivo en memoria (Debe ser ASÍNCRONO)
            file_data = await foto_perfil.read() 
            
            #Subir el archivo a Supabase Storage
            response = supabase.storage.from_(SUPABASE_BUCKET_NAME).upload(
                file=file_data,
                path=unique_filename,
                file_options={"content-type": foto_perfil.content_type}
            )
            
            #Asignar la URL pública generada
            foto_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET_NAME}/{unique_filename}"
            
        except Exception as e:
            # Manejar cualquier error de subida
            print(f"ERROR SUPABASE STORAGE: {e}") 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir la foto de perfil a Supabase Storage. Verifique permisos RLS o credenciales: {e}"
            )
        
    #Crear el objeto UsuarioCreate a partir de los datos del formulario
    usuario_data = {
        "cedula": cedula,
        "nombres_completo": nombres_completo,
        "celular": celular,
        "email": email,
        "edad": edad,
        "categoria_licencia": categoria_licencia,
        "foto_perfil_url": foto_url 
    }
    
    try:
        usuario_create = UsuarioCreate(**usuario_data)
        db_usuario = Usuario.model_validate(usuario_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la validación de datos: {e}")

    #Comprobar si ya existe
    existing_user = session.get(Usuario, db_usuario.cedula)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario con cédula {db_usuario.cedula} ya existe."
        )

    #Almacenar en la DB
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    
    #Devolver una respuesta Template para éxito
    context = {
        "request": request, 
        "usuario": db_usuario # Pasamos el objeto completo del usuario
    }
    return templates.TemplateResponse(
        "registro_exitoso.html", 
        context, 
        status_code=status.HTTP_201_CREATED
    )
#ENDPOINTS PARA VEHÍCULO (CRUD Completo)
@app.get("/vehiculos/registro", tags=["Vehiculos - Frontend"])
def get_registro_vehiculo(request: Request):
    """Muestra el formulario HTML para el registro de un nuevo vehículo."""
    context = {
        "request": request,
        "titulo_pagina": "Registro de Nuevo Vehículo"
    }
    return templates.TemplateResponse("registro_vehiculo.html", context)



@app.post("/vehiculos/", status_code=status.HTTP_201_CREATED, tags=["Vehiculos"])
async def create_vehiculo_from_form(
    request: Request,
    session: Session = Depends(get_session),
    placa: str = Form(...),
    marca: str = Form(...),
    linea: str = Form(...),
    modelo: int = Form(...),
    precio: float = Form(...),
    nivel_seguridad: int = Form(0),
    propietario_cedula: Optional[str] = Form(None), 
    
    foto_vehiculo: Optional[UploadFile] = File(None), 
):
    """
    Crea un nuevo Vehículo, procesa el formulario, sube la foto a Supabase, 
    y responde con el HTML de registro exitoso.
    """
    
    foto_url = None
    
    if foto_vehiculo and foto_vehiculo.filename:
        
        # 🚨 PROCESO DE SUBIDA REAL A SUPABASE STORAGE
        file_extension = foto_vehiculo.filename.split('.')[-1]
        unique_filename = f"vehiculos/{placa}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        
        try:
            file_data = await foto_vehiculo.read() 
            
            response = supabase.storage.from_(SUPABASE_BUCKET_NAME).upload(
                file=file_data,
                path=unique_filename,
                file_options={"content-type": foto_vehiculo.content_type}
            )
            
            foto_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET_NAME}/{unique_filename}"
            
        except Exception as e:
            print(f"ERROR SUPABASE STORAGE - VEHÍCULO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir la foto del vehículo a Supabase Storage: {e}"
            )
        
    vehiculo_data = {
        "placa": placa,
        "marca": marca,
        "linea": linea,
        "modelo": modelo,
        "precio": precio,
        "nivel_seguridad": nivel_seguridad,
        "propietario_cedula": propietario_cedula,
        "foto_url": foto_url
    }
    
    try:
        vehiculo_create = VehiculoCreate(**vehiculo_data)
        db_vehiculo = Vehiculo.model_validate(vehiculo_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la validación de datos del vehículo: {e}")

    existing_vehiculo = session.get(Vehiculo, db_vehiculo.placa)
    if existing_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vehículo con placa {db_vehiculo.placa} ya existe."
        )

    session.add(db_vehiculo)
    session.commit()
    session.refresh(db_vehiculo)
    
    context = {
        "request": request, 
        "vehiculo": db_vehiculo 
    }
    return templates.TemplateResponse(
        "exitoso_vehiculo.html", 
        context, 
        status_code=status.HTTP_201_CREATED
    )

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


# 5. ENDPOINTS PARA FICHA TÉCNICA (Relación 1:1)

@app.post("/fichas_tecnicas/", response_model=FichaTecnicaRead, status_code=status.HTTP_201_CREATED, tags=["Ficha Tecnica"])
def create_ficha_tecnica(ficha: FichaTecnicaCreate, session: Session = Depends(get_session)):
    """
    Crea la Ficha Técnica para un vehículo existente. 
    Requiere que la 'vehiculo_placa' exista y no tenga ya una ficha.
    """
    # Verificar si el vehículo existe
    vehiculo = session.get(Vehiculo, ficha.vehiculo_placa)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehículo con placa {ficha.vehiculo_placa} no encontrado.")
        
    # Verificar si ya tiene una ficha (Relación 1:1)
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

# 6. ENDPOINTS PARA COMPRA (Transacciones N:M)
@app.get("/compras/registro", tags=["Compras - Frontend"])
def get_registro_compra(request: Request):
    """Muestra el formulario HTML para registrar una nueva compra/transacción."""
    context = {
        "request": request,
        "titulo_pagina": "Registro de Nueva Compra"
    }
    return templates.TemplateResponse("registro_compra.html", context)


@app.post("/compras/", status_code=status.HTTP_201_CREATED, tags=["Compras"])
async def create_compra_from_form(
    request: Request,
    session: Session = Depends(get_session),
    comprador_cedula: str = Form(...),
    vehiculo_placa: str = Form(...),
    precio_final: float = Form(...),
    tipo_pago: str = Form(...),
):
    """
    Registra una nueva Transacción de Compra. 
    Realiza la validación cruzada: El Usuario y el Vehículo deben existir y estar activos.
    """
    
    #Verificar existencia y estado del Usuario (Comprador)
    usuario = session.get(Usuario, comprador_cedula)
    if not usuario or usuario.estado == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Usuario (Comprador) con cédula {comprador_cedula} no existe o está inactivo."
        )

    #Verificar existencia y estado del Vehículo
    vehiculo = session.get(Vehiculo, vehiculo_placa)
    if not vehiculo or vehiculo.estado == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vehículo con placa {vehiculo_placa} no existe o está inactivo."
        )
        
    #Crear el objeto Compra
    compra_data = {
        "comprador_cedula": comprador_cedula,
        "vehiculo_placa": vehiculo_placa,
        "precio_final": precio_final,
        "tipo_pago": tipo_pago,
    }
    
    try:
        compra_create = CompraCreate(**compra_data)
        db_compra = Compra.model_validate(compra_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la validación de datos de Compra: {e}")
        
    #Almacenar en la DB
    session.add(db_compra)
    session.commit()
    session.refresh(db_compra)
    
    #Devolver una respuesta Template para éxito
    context = {
        "request": request, 
        "compra": db_compra,
        "usuario": usuario,
        "vehiculo": vehiculo,
    }
    return templates.TemplateResponse(
        "exitosa_compra.html", 
        context, 
        status_code=status.HTTP_201_CREATED
    )


@app.post("/compras/", response_model=CompraRead, status_code=status.HTTP_201_CREATED, tags=["Compras"])
def create_compra(compra: CompraCreate, session: Session = Depends(get_session)):
    """
    Registra una nueva Transacción de Compra. 
    Requiere que el Usuario (comprador_cedula) y el Vehículo (vehiculo_placa) existan.
    """
    #Verificar existencia del Usuario
    usuario = session.get(Usuario, compra.comprador_cedula)
    if not usuario or usuario.estado == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Usuario (Comprador) con cédula {compra.comprador_cedula} no existe o está inactivo."
        )

    #Verificar existencia del Vehículo
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


#ENDPOINT RAIZ
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a AutoSeguro360 - API Avanzada. Consulta /docs para ver los endpoints."}

    