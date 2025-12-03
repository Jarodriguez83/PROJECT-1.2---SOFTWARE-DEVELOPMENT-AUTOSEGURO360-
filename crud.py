# crud.py
# Autor: Jhon Alexander Rodriguez Redondo
# Archivo encargado de manejar las operaciones CRUD de todos los modelos del proyecto.

from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from models import Usuario, Vehiculo, FichaTecnica, Compra


# ============================================================
# CRUD DE USUARIO
# Autor: Jhon Alexander Rodriguez Redondo
# ============================================================

def crear_usuario(session: Session, data: dict) -> Usuario:
    """
    Crea un nuevo usuario en la base de datos.
    :param session: Sesión activa de la BD
    :param data: Diccionario con los datos del usuario
    """
    usuario = Usuario(**data)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def obtener_usuario(session: Session, usuario_id: int) -> Usuario:
    """
    Obtiene un usuario por su ID.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


def listar_usuarios(session: Session, activos: bool = True):
    """
    Lista todos los usuarios.
    Si activos=True, solo retorna usuarios con estado 'activo'.
    """
    query = select(Usuario)

    if activos:
        query = query.where(Usuario.activo == True)

    usuarios = session.exec(query).all()
    return usuarios


def actualizar_usuario(session: Session, usuario_id: int, data: dict) -> Usuario:
    """
    Actualiza los datos de un usuario existente.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for key, value in data.items():
        setattr(usuario, key, value)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def eliminar_usuario(session: Session, usuario_id: int):
    """
    Soft delete: cambia el estado del usuario a inactivo.
    No elimina físicamente el registro.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = False
    session.add(usuario)
    session.commit()
    return {"mensaje": "Usuario desactivado correctamente"}



# ============================================================
# CRUD DE VEHÍCULO
# Autor: Jhon Alexander Rodriguez Redondo
# ============================================================

def crear_vehiculo(session: Session, data: dict) -> Vehiculo:
    """
    Crea un vehículo nuevo.
    Valida que la ficha técnica asociada exista si se pasa ficha_tecnica_id.
    """
    ficha_id = data.get("ficha_tecnica_id")

    if ficha_id:
        ficha = session.get(FichaTecnica, ficha_id)
        if not ficha:
            raise HTTPException(
                status_code=400,
                detail="La ficha técnica asociada no existe"
            )

    vehiculo = Vehiculo(**data)
    session.add(vehiculo)
    session.commit()
    session.refresh(vehiculo)
    return vehiculo


def obtener_vehiculo(session: Session, vehiculo_id: int) -> Vehiculo:
    """
    Obtiene un vehículo por su ID.
    """
    vehiculo = session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo


def listar_vehiculos(session: Session, activos: bool = True):
    """
    Lista vehículos.
    Si activos=True: solo muestra vehículos activos.
    """
    query = select(Vehiculo)

    if activos:
        query = query.where(Vehiculo.activo == True)

    return session.exec(query).all()


def actualizar_vehiculo(session: Session, vehiculo_id: int, data: dict) -> Vehiculo:
    """
    Actualiza los datos de un vehículo existente.
    """
    vehiculo = session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    # Validar ficha técnica si se actualiza
    ficha_id = data.get("ficha_tecnica_id")
    if ficha_id:
        ficha = session.get(FichaTecnica, ficha_id)
        if not ficha:
            raise HTTPException(
                status_code=400,
                detail="La ficha técnica asociada no existe"
            )

    for key, value in data.items():
        setattr(vehiculo, key, value)

    session.add(vehiculo)
    session.commit()
    session.refresh(vehiculo)
    return vehiculo


def eliminar_vehiculo(session: Session, vehiculo_id: int):
    """
    Soft delete: cambia el estado del vehículo a inactivo.
    """
    vehiculo = session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    vehiculo.activo = False
    session.add(vehiculo)
    session.commit()
    return {"mensaje": "Vehículo desactivado correctamente"}


# ================================
# FILTROS Y BÚSQUEDAS
# ================================

def filtrar_vehiculos(
    session: Session,
    marca: Optional[str] = None,
    linea: Optional[str] = None,
    anio_min: Optional[int] = None,
    anio_max: Optional[int] = None,
    seguridad: Optional[str] = None,
):
    """
    Filtra vehículos por marca, línea, año y nivel de seguridad.
    """
    query = select(Vehiculo).where(Vehiculo.activo == True)

    if marca:
        query = query.where(Vehiculo.marca == marca)

    if linea:
        query = query.where(Vehiculo.linea == linea)

    if anio_min:
        query = query.where(Vehiculo.modelo >= anio_min)

    if anio_max:
        query = query.where(Vehiculo.modelo <= anio_max)

    if seguridad:
        query = query.where(Vehiculo.nivel_seguridad == seguridad)

    return session.exec(query).all()


def buscar_por_linea(session: Session, linea: str):
    """
    Busca vehículos por línea (modelo comercial del carro).
    """
    query = select(Vehiculo).where(
        Vehiculo.linea.contains(linea),
        Vehiculo.activo == True
    )
    return session.exec(query).all()



# ============================================================
# CRUD DE FICHA TÉCNICA
# Autor: Jhon Alexander Rodriguez Redondo
# ============================================================

def crear_ficha_tecnica(session: Session, data: dict) -> FichaTecnica:
    """
    Crea una ficha técnica.
    Valida que no exista una ficha con la misma placa.
    """

    # Validación: placa única
    placa = data.get("placa")
    existente = session.exec(
        select(FichaTecnica).where(FichaTecnica.placa == placa)
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una ficha técnica registrada con esta placa"
        )

    ficha = FichaTecnica(**data)
    session.add(ficha)
    session.commit()
    session.refresh(ficha)
    return ficha


def obtener_ficha_tecnica(session: Session, ficha_id: int) -> FichaTecnica:
    """
    Obtiene una ficha técnica por su ID.
    """
    ficha = session.get(FichaTecnica, ficha_id)
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha técnica no encontrada")
    return ficha


def listar_fichas_tecnicas(session: Session):
    """
    Lista todas las fichas técnicas.
    """
    query = select(FichaTecnica)
    return session.exec(query).all()


def actualizar_ficha_tecnica(session: Session, ficha_id: int, data: dict) -> FichaTecnica:
    """
    Actualiza los datos de una ficha técnica.
    """

    ficha = session.get(FichaTecnica, ficha_id)
    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha técnica no encontrada"
        )

    # Validación si se cambia placa
    nueva_placa = data.get("placa")
    if nueva_placa and nueva_placa != ficha.placa:
        existente = session.exec(
            select(FichaTecnica).where(FichaTecnica.placa == nueva_placa)
        ).first()

        if existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una ficha con la placa proporcionada"
            )

    for key, value in data.items():
        setattr(ficha, key, value)

    session.add(ficha)
    session.commit()
    session.refresh(ficha)
    return ficha


def eliminar_ficha_tecnica(session: Session, ficha_id: int):
    """
    Elimina una ficha técnica de forma definitiva.
    Solo debe usarse en casos administrativos.
    """

    ficha = session.get(FichaTecnica, ficha_id)
    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha técnica no encontrada"
        )

    session.delete(ficha)
    session.commit()

    return {"mensaje": "Ficha técnica eliminada correctamente"}



# ============================================================
# CRUD DE COMPRA
# Autor: Jhon Alexander Rodriguez Redondo
# ============================================================

def crear_compra(session: Session, data: dict) -> Compra:
    """
    Crea una compra verificando:
    - Que la placa exista en Vehiculo
    - Que la cédula exista en Usuario
    - Que ambos estén activos
    """

    placa = data.get("placa")
    cedula = data.get("cedula")

    # Validar vehículo
    vehiculo = session.exec(
        select(Vehiculo).where(Vehiculo.placa == placa)
    ).first()

    if not vehiculo:
        raise HTTPException(
            status_code=404,
            detail="El vehículo con esta placa no existe"
        )

    if vehiculo.estado != "activo":
        raise HTTPException(
            status_code=400,
            detail="El vehículo no está disponible para compra"
        )

    # Validar usuario
    usuario = session.get(Usuario, cedula)
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="El usuario no existe"
        )

    if usuario.estado != "activo":
        raise HTTPException(
            status_code=400,
            detail="El usuario no está activo"
        )

    # Crear compra
    compra = Compra(**data)
    session.add(compra)
    session.commit()
    session.refresh(compra)

    return compra


def obtener_compra(session: Session, compra_id: int) -> Compra:
    """
    Obtiene una compra por su ID.
    """
    compra = session.get(Compra, compra_id)
    if not compra:
        raise HTTPException(
            status_code=404,
            detail="Compra no encontrada"
        )
    return compra


def listar_compras(session: Session):
    """
    Lista todas las compras registradas.
    """
    query = select(Compra)
    return session.exec(query).all()


def actualizar_compra(session: Session, compra_id: int, data: dict) -> Compra:
    """
    Actualiza los datos de una compra.
    """

    compra = session.get(Compra, compra_id)
    if not compra:
        raise HTTPException(
            status_code=404,
            detail="Compra no encontrada"
        )

    # Si cambian la placa → validar de nuevo
    nueva_placa = data.get("placa")
    if nueva_placa and nueva_placa != compra.placa:
        vehiculo = session.exec(
            select(Vehiculo).where(Vehiculo.placa == nueva_placa)
        ).first()

        if not vehiculo:
            raise HTTPException(
                status_code=404,
                detail="El vehículo con la nueva placa no existe"
            )

        if vehiculo.estado != "activo":
            raise HTTPException(
                status_code=400,
                detail="El vehículo no está disponible"
            )

    # Si cambian el usuario → validar también
    nueva_cedula = data.get("cedula")
    if nueva_cedula and nueva_cedula != compra.cedula:
        usuario = session.get(Usuario, nueva_cedula)
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe"
            )

        if usuario.estado != "activo":
            raise HTTPException(
                status_code=400,
                detail="El usuario no está activo"
            )

    for key, value in data.items():
        setattr(compra, key, value)

    session.add(compra)
    session.commit()
    session.refresh(compra)
    return compra


def eliminar_compra(session: Session, compra_id: int):
    """
    Elimina una compra de forma definitiva.
    """

    compra = session.get(Compra, compra_id)
    if not compra:
        raise HTTPException(
            status_code=404,
            detail="Compra no encontrada"
        )

    session.delete(compra)
    session.commit()

    return {"mensaje": "Compra eliminada correctamente"}
