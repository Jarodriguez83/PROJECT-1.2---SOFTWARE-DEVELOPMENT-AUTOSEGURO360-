from typing import List, Optional, Type
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select, SQLModel
from datetime import datetime

# Importaciones locales
from database import create_db_and_tables, get_session
from models import (
    Vehiculo, Usuario, DetalleSeguroVehiculo, 
    VehiculoCreate, VehiculoRead, VehiculoUpdate, 
    UsuarioCreate, UsuarioRead, UsuarioUpdate
)

# INICIALIZACIÓN DE FASTAPI Y CONFIGURACIÓN

def on_app_start():
    """Función para ejecutar al iniciar la aplicación."""
    create_db_and_tables()

app = FastAPI(
    title="PROYECTO AUTOSEGURO360 - LOS COCHES",
    # REQ. 1: Explicación en la documentación (Docs)
    description="""
                VENTA DE VEHÍCULOS DE SEGUNDA MANO - AUTOSEGURO360

    Esta API permite la gestión de usuarios y vehículos, aplicando las siguientes reglas de negocio:

    1.  Identificación Única Para Cada Uno de los Vehiculos por:(REQ. 1) Identificación por PLACA.
    2.  (REQ. 2) Identificación por CÉDULA para el USUARIO.
    3.  HISTORICO: (REQ. 3) La eliminación de registros se realiza mediante SOFT DELETE manejado con TRUE / FALSE.

            INSTRUCCIONES DE USO:
    - Los endpoints que buscan, actualizan o eliminan por ID ahora esperan la PLACA de los Vehículos o la CÉDULA de los Usuarios como parámetros de ruta.
    """,
    version="1.1.0",
    on_startup=[on_app_start] 
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al PROYECTO AUTOSEGURO360."}

# LÓGICA CRUD GENÉRICA Y SOFT DELETE

# REQ. 5: Manejo de Excepciones para ID no encontrado
def get_by_id(session: Session, model: Type[SQLModel], item_id: str, item_name: str) -> SQLModel:
    """Busca un ítem por ID (str: Placa o Cédula) o lanza 404."""
    item = session.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"{item_name} con ID {item_id} no encontrado")
    return item

# REQ. 2: Implementación de Soft Delete
def soft_delete(session: Session, model: Type[SQLModel], item_id: str, item_name: str):
    """Implementa la eliminación suave (soft delete) para historico."""
    item = get_by_id(session, model, item_id, item_name)
    
    item.estado = False
    item.deleted_at = datetime.utcnow()
    
    session.add(item)
    session.commit()
    return {"Mensaje": f"{item_name} con ID {item_id} marcado como inactivo (histórico guardado)"}


# VEHÍCULOS CRUD (ID=Placa)
# REQ. 1: POST (Crear)
@app.post("/vehiculos/", response_model=VehiculoRead, tags=["Vehículos"])
def create_new_vehiculo(*, session: Session = Depends(get_session), vehiculo_data: VehiculoCreate):
    """Crea un nuevo vehículo. Requiere la Placa como ID único."""
    if session.get(Vehiculo, vehiculo_data.placa):
        raise HTTPException(status_code=400, detail=f"Vehículo con placa {vehiculo_data.placa} ya existe.")
        
    vehiculo = Vehiculo.model_validate(vehiculo_data)
    session.add(vehiculo)
    session.commit()
    session.refresh(vehiculo)
    return vehiculo

# REQ. 1: GET (Listar)
@app.get("/vehiculos/", response_model=List[VehiculoRead], tags=["Vehículos"])
def list_all_vehiculos(*, session: Session = Depends(get_session), activos: Optional[bool] = Query(True, description="Filtrar por estado activo (True/False).")):
    """Lista todos los vehículos (Activos/Inactivos)."""
    query = select(Vehiculo)
    if activos is not None:
        query = query.where(Vehiculo.estado == activos)
    return session.exec(query).all()

# REQ. 1: GET (Consultar por ID/Placa)
@app.get("/vehiculos/{placa}", response_model=VehiculoRead, tags=["Vehículos"])
def get_single_vehiculo(*, session: Session = Depends(get_session), placa: str):
    """Consulta un vehículo por Placa (ID único)."""
    return get_by_id(session, Vehiculo, placa, "Vehículo")

# REQ. 1: PATCH (Actualizar)
@app.patch("/vehiculos/{placa}", response_model=VehiculoRead, tags=["Vehículos"])
def update_existing_vehiculo(*, session: Session = Depends(get_session), placa: str, vehiculo_data: VehiculoUpdate):
    """Actualiza un vehículo existente por Placa."""
    veh = get_by_id(session, Vehiculo, placa, "Vehículo")
    update_data = vehiculo_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(veh, key, value)
    
    session.add(veh)
    session.commit()
    session.refresh(veh)
    return veh

# REQ. 1 & 2: DELETE (Soft Delete)
@app.delete("/vehiculos/{placa}", tags=["Vehículos"])
def deactivate_existing_vehiculo(*, session: Session = Depends(get_session), placa: str):
    """Elimina (Soft Delete) un vehículo por Placa. Guarda histórico."""
    return soft_delete(session, Vehiculo, placa, "Vehículo")

# FILTRADO / BÚSQUEDA VEHÍCULOS
# REQ. 3: Filtrado por atributo (año)
@app.get("/vehiculos/filtro/anio/{anio}", response_model=List[VehiculoRead], tags=["Vehículos"])
def filter_vehiculos_by_anio(*, session: Session = Depends(get_session), anio: int):
    """Filtra vehículos activos por el año de fabricación."""
    query = select(Vehiculo).where(Vehiculo.anio == anio, Vehiculo.estado == True)
    return session.exec(query).all()

# REQ. 4: Búsqueda por modelo (diferente a ID)
@app.get("/vehiculos/busqueda/modelo/{modelo}", response_model=List[VehiculoRead], tags=["Vehículos"])
def search_vehiculos_by_modelo(*, session: Session = Depends(get_session), modelo: str):
    """Búsqueda de vehículos activos por modelo (coincidencia parcial)."""
    query = select(Vehiculo).where(Vehiculo.modelo.contains(modelo), Vehiculo.estado == True)
    return session.exec(query).all()

# USUARIOS CRUD (ID=Cédula)
# REQ. 1: POST (Crear)
@app.post("/usuarios/", response_model=UsuarioRead, tags=["Usuarios"])
def create_new_usuario(*, session: Session = Depends(get_session), usuario_data: UsuarioCreate):
    """Crea un nuevo usuario. Requiere la Cédula como ID único."""
    if session.get(Usuario, usuario_data.cedula):
        raise HTTPException(status_code=400, detail=f"Usuario con cédula {usuario_data.cedula} ya existe.")
        
    # REQ. 4: La categoría de licencia se establece con el valor por defecto si no se pasa.
    usuario = Usuario.model_validate(usuario_data)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

# REQ. 1: GET (Listar)
@app.get("/usuarios/", response_model=List[UsuarioRead], tags=["Usuarios"])
def list_all_usuarios(*, session: Session = Depends(get_session), activos: Optional[bool] = Query(True, description="Filtrar por estado activo (True/False).")):
    """Lista todos los usuarios (Activos/Inactivos)."""
    query = select(Usuario)
    if activos is not None:
        query = query.where(Usuario.estado == activos)
    return session.exec(query).all()

# REQ. 1: GET (Consultar por ID/Cédula)
@app.get("/usuarios/{cedula}", response_model=UsuarioRead, tags=["Usuarios"])
def get_single_usuario(*, session: Session = Depends(get_session), cedula: str):
    """Consulta un usuario por Cédula (ID único)."""
    return get_by_id(session, Usuario, cedula, "Usuario")

# REQ. 1: PATCH (Actualizar)
@app.patch("/usuarios/{cedula}", response_model=UsuarioRead, tags=["Usuarios"])
def update_existing_usuario(*, session: Session = Depends(get_session), cedula: str, usuario_data: UsuarioUpdate):
    """Actualiza un usuario existente por Cédula."""
    user = get_by_id(session, Usuario, cedula, "Usuario")
    update_data = usuario_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# REQ. 1 & 2: DELETE (Soft Delete)
@app.delete("/usuarios/{cedula}", tags=["Usuarios"])
def deactivate_existing_usuario(*, session: Session = Depends(get_session), cedula: str):
    """Elimina (Soft Delete) un usuario por Cédula. Guarda histórico."""
    return soft_delete(session, Usuario, cedula, "Usuario")

# REQ. 5: BÚSQUEDA USUARIOS POR LICENCIA
@app.get("/usuarios/busqueda/licencia/{categoria}", response_model=List[UsuarioRead], tags=["Usuarios"])
def search_usuarios_by_licencia_categoria(*, session: Session = Depends(get_session), categoria: str):
    """Busca usuarios activos por categoría de licencia. (Ejemplo: 'A2', 'B1', o '0')."""
    query = select(Usuario).where(Usuario.categoria_licencia == categoria, Usuario.estado == True)
    return session.exec(query).all()