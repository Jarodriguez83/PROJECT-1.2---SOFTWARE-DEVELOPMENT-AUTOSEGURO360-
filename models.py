from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

# MODELO USUARIO (ID=Cédula, incluye categoría de licencia)
class UsuarioBase(SQLModel):
    """Base para Usuario."""

    cedula: str = Field(primary_key=True, index=True, description="Cédula del usuario, es el ID único")
    nombres: str
    apellidos: str
    correo: str = Field(unique=True)
    telefono: Optional[str] = None
    
    # REQ. 4: Categoría de pase integrada. "0" si no tiene.
    categoria_licencia: str = Field(default="0", description="Categoría del pase de conducción. '0' si no tiene.")
    fecha_vencimiento_licencia: Optional[datetime] = None
    
class Usuario(UsuarioBase, table=True):
    # REQ. 2: Campo de estado para el histórico (soft delete)
    estado: bool = Field(default=True, description="True=activo, False=inactivo (soft delete)")
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None 
    
    # RELACIÓN 1:N con Vehiculo
    vehiculos: List["Vehiculo"] = Relationship(back_populates="propietario")


# ==================================================
# TABLA INTERMEDIA: VEHICULO <-> DETALLE SEGURO (N:M)
# ==================================================
class DetalleSeguroVehiculo(SQLModel, table=True):
    """Tabla de enlace N:M para los detalles de seguro/técnico-mecánica."""
    # La FK usa la placa del vehículo
    vehiculo_placa: str = Field(foreign_key="vehiculo.placa", primary_key=True)
    tipo_seguro: str = Field(primary_key=True, description="Tipo: SOAT, TecnoMecanica, TodoRiesgo")
    estado_vigencia: str = Field(description="Activo o Vencido")
    fecha_revision: datetime = Field(default_factory=datetime.utcnow)
    
    # RELACIÓN N:M con Vehiculo
    vehiculo: "Vehiculo" = Relationship(back_populates="detalles_seguro")


# ==================================================
# MODELO VEHÍCULO
# ==================================================
class VehiculoBase(SQLModel):
    """Base para Vehiculo."""
    # REQ. 2: PLACA ES EL ID PRIMARIO
    placa: str = Field(primary_key=True, description="Placa del vehículo, es el ID único")
    
    marca: str
    modelo: str
    anio: int
    precio: float
    calificacion_latin_ncap: Optional[int] = Field(default=0, description="Calificación de seguridad (0 a 5 estrellas)")

class Vehiculo(VehiculoBase, table=True):
    # Clave Foránea 1:N con Usuario (ID=cedula)
    propietario_cedula: Optional[str] = Field(default=None, foreign_key="usuario.cedula") 
    
    # REQ. 2: Campo de estado para el histórico (soft delete)
    estado: bool = Field(default=True, description="True=activo, False=inactivo (soft delete)")
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None 
    
    # RELACIÓN N:1 con Usuario (propietario)
    propietario: Optional[Usuario] = Relationship(back_populates="vehiculos")
    # RELACIÓN N:M con DetalleSeguroVehiculo
    detalles_seguro: List[DetalleSeguroVehiculo] = Relationship(back_populates="vehiculo")
    

# ESQUEMAS PARA CREACIÓN Y LECTURA (Pydantic)

# Esquemas de lectura
class UsuarioRead(UsuarioBase):
    estado: bool
    fecha_registro: datetime
    
class VehiculoRead(VehiculoBase):
    propietario_cedula: Optional[str] = None
    estado: bool
    fecha_registro: datetime
    
# *** CORRECCIÓN: Definición explícita de esquemas Create ***
class UsuarioCreate(UsuarioBase):
    """Esquema para crear un nuevo usuario."""
    pass

class VehiculoCreate(VehiculoBase):
    """Esquema para crear un nuevo vehículo."""
    propietario_cedula: Optional[str] = None
    pass
    
# Esquemas de actualización
class UsuarioUpdate(SQLModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    categoria_licencia: Optional[str] = None
    fecha_vencimiento_licencia: Optional[datetime] = None
    
class VehiculoUpdate(SQLModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    precio: Optional[float] = None
    propietario_cedula: Optional[str] = None
    calificacion_latin_ncap: Optional[int] = None