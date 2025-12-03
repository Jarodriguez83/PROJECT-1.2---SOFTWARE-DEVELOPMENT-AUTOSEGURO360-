"""
models.py
Autor: Jhon Alexander Rodriguez Redondo

Definición de los 4 modelos (Usuario, Vehiculo, FichaTecnica, Compra) y sus relaciones:
- Usuario (PK=Cédula) y Vehiculo (PK=Placa) como bases de identidad.
- Vehiculo <-> FichaTecnica (Relación 1:1, garantizada por PK/FK).
- Usuario <-> Compra <-> Vehiculo (Relación N:M, Histórico de transacciones).
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

# ==================================================
# 1. MODELO USUARIO (ID=Cédula, incluye multimedia y estado)
# ==================================================
class UsuarioBase(SQLModel):
    """Base para Usuario."""
    cedula: str = Field(primary_key=True, index=True, description="Cédula del usuario, es el ID único (PK)")
    nombres_completo: str
    celular: str
    email: str = Field(unique=True)
    edad: int
    categoria_licencia: str = Field(default="0", description="Categoría del pase de conducción. '0' si no tiene.")
    foto_perfil_url: Optional[str] = Field(default=None, description="URL o ruta a la foto de perfil (Multimedia)")
    
class Usuario(UsuarioBase, table=True):
    estado: bool = Field(default=True, description="True=activo, False=inactivo (soft delete)")
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
    
    # RELACIONES
    # 1:N con Compra (un usuario puede tener muchas compras/ventas)
    compras: List["Compra"] = Relationship(back_populates="comprador")

# ==================================================
# 2. MODELO VEHÍCULO (ID=Placa, incluye multimedia y estado)
# ==================================================
class VehiculoBase(SQLModel):
    """Base para Vehiculo (Datos comerciales)."""
    placa: str = Field(primary_key=True, description="Placa del vehículo, es el ID único (PK)")
    marca: str
    linea: str
    modelo: int # Año de fabricación
    precio: float
    foto_url: Optional[str] = Field(default=None, description="URL o ruta a la foto del vehículo (Multimedia)")
    nivel_seguridad: Optional[int] = Field(default=0, description="Calificación de seguridad (ej. Latin NCAP)")

class Vehiculo(VehiculoBase, table=True):
    estado: bool = Field(default=True, description="True=activo, False=inactivo (soft delete)")
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
    
    # RELACIONES
    # 1:1 con FichaTecnica (Un vehículo tiene exactamente una ficha técnica)
    ficha_tecnica: Optional["FichaTecnica"] = Relationship(back_populates="vehiculo")
    # 1:N con Compra (un vehículo puede tener muchas compras/ventas)
    compras: List["Compra"] = Relationship(back_populates="vehiculo_transaccion")


# ==================================================
# 3. MODELO FICHA TÉCNICA (Relación 1:1 con Vehiculo)
# ==================================================
class FichaTecnicaBase(SQLModel):
    """Base para Ficha Técnica (Datos técnicos)."""
    cilindraje: Optional[int] = None
    color: Optional[str] = None
    tipo_servicio: Optional[str] = None
    tipo_carroceria: Optional[str] = None
    clase_vehiculo: Optional[str] = None
    combustible: Optional[str] = None
    capacidad: Optional[int] = None
    potencia_hp: Optional[int] = None

class FichaTecnica(FichaTecnicaBase, table=True):
    # Clave Foránea y Primaria para asegurar la relación 1:1
    # La FK es la Placa del Vehículo
    vehiculo_placa: str = Field(foreign_key="vehiculo.placa", primary_key=True) 

    # Relación Inversa N:1 (Ficha Técnica -> Vehículo)
    vehiculo: Vehiculo = Relationship(back_populates="ficha_tecnica")


# ==================================================
# 4. MODELO COMPRA (Transacción N:M, Histórico de dueños)
# ==================================================
class CompraBase(SQLModel):
    """Base para Compra (Transacción)."""
    precio_final: float
    tipo_pago: str = Field(default="Efectivo")
    fecha_compra: datetime = Field(default_factory=datetime.utcnow)

class Compra(CompraBase, table=True):
    # ID Propio para la transacción (PK)
    id: Optional[int] = Field(default=None, primary_key=True)
    estado: str = Field(default="Completada", description="Estado de la transacción (Completada, Cancelada, Pendiente)")
    
    # Claves Foráneas N:1 (Definen la relación N:M entre Usuario y Vehiculo)
    comprador_cedula: str = Field(foreign_key="usuario.cedula", index=True) 
    vehiculo_placa: str = Field(foreign_key="vehiculo.placa", index=True)
    
    # RELACIONES INVERSAS
    # N:1 con Usuario (Comprador)
    comprador: Usuario = Relationship(back_populates="compras")
    # N:1 con Vehiculo
    vehiculo_transaccion: Vehiculo = Relationship(back_populates="compras")


# ==================================================
# ESQUEMAS PARA CREACIÓN Y LECTURA (Pydantic)
# ==================================================

# Esquemas de Lectura
class UsuarioRead(UsuarioBase):
    estado: bool
    fecha_registro: datetime
    
class VehiculoRead(VehiculoBase):
    estado: bool
    fecha_registro: datetime

class FichaTecnicaRead(FichaTecnicaBase):
    vehiculo_placa: str

class CompraRead(CompraBase):
    id: int
    estado: str
    comprador_cedula: str
    vehiculo_placa: str

# Esquemas de Creación
class UsuarioCreate(UsuarioBase):
    pass

class VehiculoCreate(VehiculoBase):
    pass
    
# FichaTecnicaCreate debe incluir la clave foránea
class FichaTecnicaCreate(FichaTecnicaBase):
    vehiculo_placa: str

class CompraCreate(CompraBase):
    comprador_cedula: str
    vehiculo_placa: str


# Esquemas de Actualización (Opcionales)
class UsuarioUpdate(SQLModel):
    nombres_completo: Optional[str] = None
    celular: Optional[str] = None
    email: Optional[str] = None
    edad: Optional[int] = None
    categoria_licencia: Optional[str] = None
    foto_perfil_url: Optional[str] = None
    
class VehiculoUpdate(SQLModel):
    marca: Optional[str] = None
    linea: Optional[str] = None
    modelo: Optional[int] = None
    precio: Optional[float] = None
    foto_url: Optional[str] = None
    nivel_seguridad: Optional[int] = None

class FichaTecnicaUpdate(FichaTecnicaBase):
    # La placa no se actualiza
    pass 

class CompraUpdate(SQLModel):
    precio_final: Optional[float] = None
    tipo_pago: Optional[str] = None
    estado: Optional[str] = None